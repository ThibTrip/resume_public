"""
Runs a web application for my resume. Uses the following resources:

* /templates: folder of Jinja2 templates
* /static: images, css, javascript code
* data local to this script (mostly dataclasses) that is passed to templates

All the resources are self-hosted (except for Python libraries)
to make sure that this app can always run.

This script is formatted to be read as a notebook using
https://github.com/mwouts/jupytext

Author: Thibault Betremieux
"""
from __future__ import annotations
import argparse
import datetime
import os
from dataclasses import dataclass, field as dataclass_field
from flask import Flask, render_template, request


# region Helpers

@dataclass(frozen=True)
class ProgressSkill:
    """
    Data for a skill using a bootstrap progress element

    Parameters
    ----------
    label
        What is shown on the left side of the bar
        e.g. "French" (for showing the proficiency in this language)
    progress
        Width of the progress bar, 100 being completely full
    icon_name
        Name of the icon to use on the left of the `label`
        (see folder `static/icons`)
    label_bar
        Optional label to put on the bar itself
    color
        Which color to use for the progress bar
    """
    label: str
    progress: int
    icon_name: str
    label_bar: str = dataclass_field(default='')
    color: str = dataclass_field(default='#7f8d63')


@dataclass(frozen=True)
class TextSkill:
    """
    Data for a skill displayed as text in my resume

    Parameters
    ----------
    title
        A title for the skill e.g. "Data transformation"
    items
        List of sentences explaining the experience (each sentence
        will be rendered as HTML <li> element, unless there
        is only one sentence in which case we use <p>)
    """
    title: str
    items: list[str]


@dataclass(frozen=True)
class Experience:
    """
    Job, internship or study in my resume

    Parameters
    ----------
    title
        A title for the core skill e.g. "Data transformation"
    name
        Company or school name
    date_range
        Date range as a string e.g. "10.2014 – 04.2016"
    location
        E.g. city
    items
        List of sentences explaining the experience (each sentence
        will be rendered as HTML <li> element, unless there
        is only one sentence in which case we use <p>)
    icon_name
        Name of the icon to use on the left of the `label`
        (see folder `static/icons`)
    """
    title: str
    name: str
    date_range: str
    location: str
    items: list[str]
    icon_name: str | None = dataclass_field(default=None)


def get_extra_files(extra_dirs: list[str]) -> list[str]:
    """
    Gets a list of "extra" files to be monitored by flask and reloaded
    on changes when doing live development.
    See https://stackoverflow.com/a/9511655/10551772

    Examples
    --------
    >>> get_extra_files(extra_dirs=['./static', './templates'])  # doctest: +ELLIPSIS
    ['./static', './templates', ..., './static/icons/FR.svg', ..., './templates/index.html', ...]
    """
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    return extra_files


# endregion Helpers

# region Data

# Encoded email to avoid spam
# See http://hcard.geekhood.net/encode/
ENCODED_EMAIL = ('t&#x68;&#x69;ba&#x75;l&#x74;&#x2E;&#98;etr&#x65;&#x6d;i&#101;&#x75;x&#x40;&#x67;&#x6D;ail&#46;'
                 '&#x63;&#111;&#x6D;')

# variables sorted as they appear in the web page (from top to bottom or left to right if in the same container)

# region Progress skills

languages = [ProgressSkill(label='Französisch', progress=100, icon_name='FR.svg', label_bar='C2'),
             ProgressSkill(label='Englisch', progress=100, icon_name='GB.svg', label_bar='C1'),
             ProgressSkill(label='Deutsch', progress=90, icon_name='DE.svg', label_bar='C1'),
             ProgressSkill(label='Italienisch', progress=80, icon_name='IT.svg', label_bar='B2'),
             ProgressSkill(label='Ukrainisch', progress=60, icon_name='UA.svg', label_bar='B1'),
             ProgressSkill(label='Russisch', progress=60, icon_name='RU.png', label_bar='B1')]

programming_languages = [ProgressSkill(label='Python', progress=95, icon_name='python.png'),
                         ProgressSkill(label='SQL', progress=60, icon_name="postgresql.svg"),
                         ProgressSkill(label='Bash', progress=15, icon_name='bash.png'),
                         ProgressSkill(label='Java', progress=10, icon_name='java.png')]

tools = [ProgressSkill(label='Jupyter Lab', progress=90, icon_name='jupyterlab.png'),
         ProgressSkill(label='Odoo', progress=85, icon_name='odoo-square.png'),
         ProgressSkill(label='Tableau', progress=85, icon_name='tableau.png'),
         ProgressSkill(label='Excel', progress=60, icon_name='excel.png'),
         ProgressSkill(label='AWS', progress=25, icon_name='aws.png'),
         ProgressSkill(label='Docker', progress=10, icon_name='docker.png')]

markup_languages = [ProgressSkill(label='Markdown', progress=90, icon_name="markdown.png"),
                    ProgressSkill(label='HTML|CSS', progress=20, icon_name="html_css.png")]

# endregion Progress skills

# region Core skills

data_wrangling = TextSkill(title='Datenverarbeitung in Python',
                           items=['<b>Tabellentransformierung</b> mit '
                                  '<a href="https://pandas.pydata.org/">pandas</a>',

                                  '<b>SQL</b> Modellierung und Workflows mit '
                                  '<a href="https://www.sqlalchemy.org/">sqlalchemy</a>',

                                  'Mit vielen <b>verschiedenen Datenquellen</b> arbeiten '
                                  '(SQL, REST und SOAP API, Excel, CSV, ...)'])

library_dev = TextSkill(title='Entwicklung von Bibliotheken und Scripte',
                        items=['<b>Testing</b> mit <a href="https://docs.pytest.org/">pytest</a> '
                               '(inkl. coverage und doctest)',

                               '<b>Dokumentation</b> (numpydoc guide style, GitHub Wiki)',

                               '<b>Maintenance</b> (Commits, Tags, Releases, Issues, PR,...)'])

data_viz = TextSkill(title='Datenvisualisierung',
                     items=['Gestaltung von <b>komplexen <a href="https://www.tableau.com/">Tableau</a> '
                            'Dashboards</b> mit Hilfe von <b>Python</b> und <b>SQL</b>'])

webscraping = TextSkill(title='Webscraping',
                        items=['Automatische <b>Navigation und Datenextrahierung</b> auf Internetseiten '
                               'mit Tools wie <a href="https://playwright.dev/">Microsoft Playwright</a>'])

# endregion Core skills

# region Soft skills

soft_skills = [TextSkill(title='Softskills',
                         items=['Eigeninitiative',
                                'Zuverlässigkeit',
                                'Teamplayer und soziale Kompetenzen im Umgang mit verschiedenen Gesprächspartnern',
                                'Arbeitspraxis im internationalen Umfeld',
                                'Sehr gute schriftliche und mündliche Kommunikationsfähigkeit'])]

# endregion Soft skills

# endregion Data

# region Jobs

jobs = [Experience(title='Senior Python Software Developer',
                   name='JobRad GmbH',
                   date_range='08.2022 - jetzt',
                   location='Freiburg-im-Breisgau',
                   icon_name='JobRad.png',
                   items=['Entwicklung und Integration eines maßgeschneiderten und <b>funktionsreichen '
                          'Ereignissystems</b> für JobRad, inklusive nahtloser Anbindung an externe Systeme '
                          'wie APIs und Salesforce',

                          'Schlüsselrolle bei der Entwicklung und Wartung von Legacy und bzw. neuen <b>APIs</b>, '
                          'um <b>Robustheit</b> und Skalierbarkeit zu gewährleisten',

                          'Engagierte Mitarbeit in einem <b>agilen Team</b> durch Pair-Programming und strategische '
                          'Entwicklungsmeetings zur Steigerung der Projektqualität',

                          'Einsatz für <b>Clean Code</b> durch fortlaufendes <b>Refactoring</b>, ausführliche '
                          '<b>Dokumentation</b> und Einführung von Code-Analyse-Tools wie SonarQube']),
        Experience(title='Data Analyst',
                   name='port-neo GmbH',
                   date_range='01.2018 - 07.2022',
                   location='Freiburg-im-Breisgau',
                   icon_name='port_neo_wx60.png',
                   items=['Erfassung, Aufbereitung und Export von Marketing- und Controllingdaten aus diversen '
                          'Quellen wie Newsletterdaten, CRM und APIs',

                          '<b>Entwicklung und Pflege von über 30 Python-Bibliotheken</b> zur Lösung spezifischer '
                          'Datenverarbeitungsprobleme wie Datenbereinigung (u.a. Kodierung, Duplikatbereinigung, '
                          'Geodatenbereinigung) und Datenanreicherung (z.B. Geocodierung)',

                          'Implementierung automatisierter Datenworkflows unter Einsatz von <b>AWS, Docker, cron jobs '
                          'und systemd</b>, um Effizienz und Zuverlässigkeit zu steigern',

                          '<b>Design von Marketing-Dashboards mit Tableau</b>, spezialisiert auf Newsletter- und '
                          'personenbezogenen Daten, zur Unterstützung datengetriebener Entscheidungen']),
        Experience(title='Junior Online Marketing Manager (befristet)',
                   name='TANDEM Kommunikation GmbH',
                   date_range='06.2017 – 11.2017',
                   location='Freiburg-im-Breisgau',
                   icon_name='tandem_wx60.png',
                   items=['Implementierung von Tools wie <b>Google Analytics</b> und Tag Manager auf <b>über 25 '
                          'Websites</b> um Website Daten zu erheben',

                          'Häufige Arbeit mit Daten von <b>AdWords</b> um Konten zu optimieren, teilweise mit Python']),
        Experience(title='Junior Account Manager Online Marketing (befristet)',
                   name='exito GmbH & Co. KG',
                   date_range='08.2016 – 12.2016',
                   location='Nürnberg',
                   icon_name='exito_wx60.png',
                   items=['Entwicklung und Analyse von <b>SEA-Kundenkampagnen</b> auf Französisch und Italienisch, '
                          'inkl. Berichterstattung für Kunden',

                          'Gestaltung bzw. Auswahl von <b>Anzeigentexten</b>, <b>Keywords</b> und <b>Landing Pages</b>',

                          'Verantwortung für <b>Budgetmanagement</b> und -optimierung der Kampagnen, orientiert an '
                          '<b>Performancezielen</b>'])]

jobs_page_2 = [Experience(title='Projektmanager (befristet)',
                          name='Arbeit und Leben NRW',
                          date_range='05.2015 – 04.2016',
                          location='Düsseldorf',
                          icon_name='aulnrw_wx60.png',
                          items=['<b>Organisation</b> und <b>Begleitung</b> von <b>10 Begegnungen</b> zwischen '
                                 '<b>deutschen und französischen</b> Auszubildenden',

                                 '<b>Leitung vor Ort</b> von einigen dieser Begegnungen und Ausbildung „interkultureller '
                                 'Jugendleiter“',

                                 'Mitwirkung beim Aufbau von <b>Partnerschaften</b> zwischen Arbeit und Leben NRW und '
                                 'verschiedenen berufsbildenden sowie sozialpolitisch engagierten Organisationen'])]

# endregion Jobs

# region Studies

studies = [Experience(title='Fachausbildung in Online-Handel und Online Marketing',
                      name='Hochschule Conservatoire National des Arts et Métiers - 5 Zertifikate',
                      date_range='10.2014 – 04.2016',
                      location='Paris, Frankreich (Fernunterricht)',
                      items=['E-Werbung und Kommunikation',
                             'E-Handel',
                             'Sammlung und Verarbeitung von E-Marketing Daten',
                             'Entscheidende Statistiken in Marketing',
                             'Elektronische Marketing – Digital Marketing']),
           Experience(title='Doppel-Master of Arts „Internationale Wirtschaftsbeziehungen“',
                      name='Albert-Ludwigs-Universität Freiburg',
                      date_range='10. 2012 - 09. 2014', location='Freiburg-im-Breisgau',
                      items=['Masterarbeit „Das legislative Umfeld des Bio-Sektors“ (Sept. 2014, 77 S. auf Deutsch)']),
           Experience(title='Doppel-Master of Arts „Commerce et Affaires internationales“ (International Business)',
                      name='Université Paris Est Créteil (UPEC)', date_range='10. 2012 - 09. 2014',
                      location='Créteil, Frankreich',
                      items=['Bericht „Qualität und Ausbildung“ als Vorbereitung auf ein '
                             'Praktikum beim Dialoge Sprachinstitut (Sept. 2013, 35 S. auf Französisch)']),
           Experience(title='Viersprachiger Bachelor of Arts „Internationaler Handel“',
                      name='Université Paris Est Créteil (UPEC)',
                      date_range='10.2009 - 08.2012', location='Créteil, Frankreich', items=[]),
           Experience(title='Baccalauréat (Sciences de l’Ingénieur) = Abitur (Ingenieurwissenschaften)',
                      name='Lycée d’Arsonval',
                      date_range='10.2009 - 08.2012', location='Saint Maur des Fossés, Frankreich', items=[])]

# endregion Studies

# region Internships

internships = [Experience(title='Assistent der Schulleitung',
                          name='Dialoge Sprachinstitut GmbH, Master Praktikum',
                          date_range='09. 2013 – 01.2014',
                          location='Lindau',
                          items=['Kundenbetreuung und Marketing',
                                 'Wettbewerbsanalyse und Suche nach potenziellen Kunden',
                                 '<b>Qualitätsmanagement</b>: Datenverarbeitung und Erstellung von Dokumenten für die '
                                 'ISO 9001 Akkreditierung']),
               Experience(title='Assistent des Teams Insolvenzverwalterbetreuung',
                          name='HSBC Trinkaus & Burkhardt AG Firmenkunden Bereich, Bachelor Praktikum',
                          date_range='05.2012 – 08.2012',
                          location='Düsseldorf',
                          items=['Einblick in die Richtlinien der Eigenkapitalunterlegung, Insolvenzgeldfinanzierung '
                                 'und Treuhandkontenverwaltung',

                                 'Unterstützung des Teams “Insolvenzverwalterbetreuung” bei Treuhandkonteneröffnung '
                                 'und Terminkontrolle von Insolvenzverfahren Abfrage von neuen Insolvenzverfahren'])]

# endregion Internships

# region Holiday jobs

holiday_jobs = [Experience(title='Assistent Back Office',
                           name='HSBC Business Banking',
                           date_range='08.2011',
                           location='Saint-Maur-des-Fossés, Frankreich',
                           items=['Hilfe bei der Vorbereitung den finanziellen Dokumenten im Rahmen von '
                                  'Ausschreibungen.']),
                Experience(title='Assistent Back Office',
                           name='Société Générale',
                           date_range='08.2010',
                           location='Sucy-en-Brie, Frankreich',
                           items=['Archivierung von Dokumenten, Kontenschließung und -Eröffnung und Überprüfung '
                                  'von Kundendaten.'])]

# endregion Holiday jobs


# create the app
app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}


@app.route('/')
def index():
    return render_template('index.html',
                           encoded_email=ENCODED_EMAIL,
                           # trick to bust CSS caching (we'll use that as a param for the URL)
                           cache_bust=str(int(datetime.datetime.now().timestamp())),
                           # 1. top page
                           # core skills
                           data_wrangling=data_wrangling,
                           library_dev=library_dev,
                           data_viz=data_viz,
                           webscraping=webscraping,
                           # progress skills
                           languages=languages,
                           programming_languages=programming_languages,
                           tools=tools,
                           markup_languages=markup_languages,
                           # soft skills
                           soft_skills=soft_skills,
                           # 2. bottom page
                           jobs=jobs,
                           jobs_page_2=jobs_page_2,
                           internships=internships,
                           studies=studies,
                           holiday_jobs=holiday_jobs)


# Start the App
if __name__ == '__main__':
    # for development, we are going to need debug for reloading
    # python code and data within it
    # add a debug flag for the CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # run the app
    app.run(debug=args.debug, extra_files=get_extra_files(['./templates', './static']))
