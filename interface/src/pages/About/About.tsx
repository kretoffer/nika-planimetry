import * as React from 'react';

export const About = () => {
    return (
        <div className="about-page-container">
            <div className="about-page">
                <h1 className="about-page-text" style={{textAlign: "justify", marginLeft: "100px", marginRight: "100px"}}>
                    Обучающая диалоговая экспертная система <b>NIKA</b> (<b>N</b>ika is an <b>I</b>ntelligent <b>K</b>nowledge-driven <b>A</b>ssistant),
                    разработанный на основе технологии{' '}
                        <a href="http://ims.ostis.net/" className="text">
                          OSTIS
                        </a>
                    . Обучающая диалоговая экспертная ostis-система NIKA предназначена для упрощения изучения планиметрии.
                </h1>
            </div>
        </div>
    );
}
