"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""
import logging
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_client.constants import sc_type
from sc_client.client import search_by_template

from sc_kpm import ScAgentClassic, ScResult
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    generate_link,
    get_link_content_data,
    check_connector, generate_connector,
    erase_connectors,
    search_element_by_non_role_relation,
    get_element_system_identifier,
    search_connector
)
from sc_kpm.utils.action_utils import (
    generate_action_result,
    finish_action_with_status,
    get_action_arguments,
)
from sc_kpm import ScKeynodes

import requests
from typing import List
from random import choice


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class TaskAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_get_task")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info("TaskAgent finished %s",
                         "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("TaskAgent started")

        try:
            message_addr = get_action_arguments(action_node, 1)[0]
            self.logger.info(get_element_system_identifier(message_addr))
            message_type = ScKeynodes.resolve(
                "concept_message_about_task_of_theme", sc_type.CONST_NODE_CLASS)

            if not check_connector(sc_type.VAR_PERM_POS_ARC, message_type, message_addr):
                self.logger.info(
                    f"TaskAgent: the message isn’t about task")
                return ScResult.OK

            
            
            
            idtf = ScKeynodes.resolve("nrel_idtf", sc_type.CONST_NODE_NON_ROLE)
            answer_phrase = ScKeynodes.resolve(
                "get_task_answer_phrase", sc_type.CONST_NODE_CLASS)
            rrel_entity = ScKeynodes.resolve("rrel_entity", sc_type.CONST_NODE_ROLE)
            rrel_response = ScKeynodes.resolve(
                "rrel_response", sc_type.CONST_NODE_ROLE)

            theme_addr = self.get_entity_addr(
                message_addr, rrel_entity)
            idtff = get_element_system_identifier(theme_addr)
            self.logger.info(f"Detected entity {idtff}")

            if not theme_addr.is_valid() or not idtff:
                self.set_unknown_theme_link(action_node, message_addr, rrel_response)
                return ScResult.OK

            self.clear_previous_answer(
                theme_addr, rrel_response, answer_phrase)
            
            tasks = self.get_tasks_of_theme(theme_addr)
            links = [task.get(2) for task in tasks]
            
            task = self.select_task(links, "нормально")
            
            _idtf = get_link_content_data(self.search_lang_value_by_nrel_identifier(task, "nrel_idtf"))
            _main_idtf = get_link_content_data(self.get_ru_main_identifier(task))
            _level = get_link_content_data(self.search_lang_value_by_nrel_identifier(task, "nrel_task_level"))
            _condition = get_link_content_data(self.search_lang_value_by_nrel_identifier(task, "nrel_condition"))



            text = f"""
                <h2>{_idtf}</h2>
                <h3>Уровень задачи: <b>{_level}</b></h3>

                {_condition}
                <br><br>
                Если будут проблемы с решением, напиши мне <i>"Как решить {_main_idtf}"</i> и я тебе помогу
            """

            link = generate_link(text, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK)
            edge = generate_connector(sc_type.CONST_COMMON_ARC, message_addr, link)
            generate_connector(sc_type.CONST_PERM_POS_ARC, rrel_response, edge)
            generate_action_result(action_node, link)

            return ScResult.OK


        except Exception as e:
             self.logger.info(f"TaskAgent: finished with an error {e}")
             return ScResult.ERROR


    def set_unknown_theme_link(self, action_node: ScAddr, message_addr: ScAddr, rrel_response: ScAddr) -> None:
        text = "Извините, но к сожалению, я не знаю эту тему"
        link = generate_link(text, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK)
        edge = generate_connector(sc_type.CONST_COMMON_ARC, message_addr, link)
        generate_connector(sc_type.CONST_PERM_POS_ARC, rrel_response, edge)
        generate_action_result(action_node, link)


    def get_ru_main_identifier(self, entity_addr: ScAddr) -> ScAddr:
        return self.search_lang_value_by_nrel_identifier(entity_addr, "nrel_main_idtf", "lang_ru")
    
    def search_lang_value_by_nrel_identifier(self, entity_addr: ScAddr, idtf_str: str = "nrel_main_idtf", lang_str: str = "lang_ru") -> ScAddr:
        idtf = ScKeynodes.resolve(
            idtf_str, sc_type.CONST_NODE_NON_ROLE)
        lang = ScKeynodes.resolve(lang_str, sc_type.CONST_NODE_CLASS)

        template = ScTemplate()
        template.quintuple(
            entity_addr,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            idtf,
        )
        search_results = search_by_template(template)
        if len(search_results) == 1:
            return search_results[0][2]
        for result in search_results:
            idtf = result[2]
            lang_edge = search_connector(
                lang, idtf, sc_type.VAR_PERM_POS_ARC)
            if lang_edge:
                return idtf
        return search_element_by_non_role_relation(
            src=entity_addr, nrel_node=idtf)

    def get_entity_addr(self, message_addr: ScAddr, rrel_entity: ScAddr) -> ScAddr:
        rrel_entity = ScKeynodes.resolve("rrel_entity", sc_type.CONST_NODE_ROLE)
        concept_theme = ScKeynodes.resolve(
            "concept_theme", sc_type.CONST_NODE_CLASS)
        template = ScTemplate()
        # entity node or link
        template.quintuple(
            message_addr,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR,
            sc_type.VAR_PERM_POS_ARC,
            rrel_entity,
        )
        search_results = search_by_template(template)
        if len(search_results) == 0:
            return ScAddr(0)
        entity = search_results[0][2]
        if len(search_results) == 1:
            return entity
        else:
            self.logger.info("More then 1 arg")
            return ScResult.ERROR
        
    def get_task_level(self, task: ScAddr) -> str:
        return get_link_content_data(self.search_lang_value_by_nrel_identifier(task, "nrel_task_level", "lang_ru"))
        
    def select_task(self, tasks: List[ScAddr], level: str):
        level_tasks = [task if self.get_task_level(task) == level else None for task in tasks]
        result_tasks = [task for task in level_tasks if task is not None]
        return choice(result_tasks)
        
        
    def get_tasks_of_theme(self, theme: ScAddr):
        nrel_task_theme = ScKeynodes.resolve(
            "nrel_task_theme", sc_type.CONST_NODE_NON_ROLE)
        template = ScTemplate()
        template.quintuple(
            theme,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            nrel_task_theme
        )
        search_results = search_by_template(template)
        return search_results

    def clear_previous_answer(self, entity, nrel_response, answer_phrase):
        message_answer_set = ScSet(set_node=answer_phrase)
        message_answer_set.clear()
        if not entity.is_valid():
            return

        template = ScTemplate()
        template.quintuple(
            entity,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            nrel_response
        )
        search_results = search_by_template(template)
        for result in search_results:
           erase_connectors(result[0], result[2], sc_type.VAR_COMMON_ARC)
