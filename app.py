# -*- coding: utf-8 -*-
"""
Runs a web application for my resume. Uses the following resources:

* /templates: folder of Jinja2 templates
* /static: images, css, javascript code
* data local to this script (mostly dataclasses) that is passed to templates

All the resources are self hosted (except for Python libraries)
to make sure that this app can always run.

This script is formatted to be read as a notebook using
https://github.com/mwouts/jupytext

Author: Thibault Betremieux
"""
import argparse
import datetime
import os
from dataclasses import dataclass, field as dataclassfield
from flask import Flask, render_template, request
from typing import List, Optional


# # Helpers

# +
@dataclass(frozen=True)
class ProgressSkill:
    """
    Data for a skill using a bootstrap progress element

    Parameters
    ----------
    label
        Label we will put on the left side of the bar
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
    label:str
    progress:int
    icon_name:str
    label_bar:str = dataclassfield(default='')
    color:str = dataclassfield(default='#7f8d63')


@dataclass(frozen=True)
class TextSkill:
    """
    Data for a skill displayed as text in my resume

    Parameters
    ----------
    title
        Title of the skill e.g. "Data transformation"
    items
        List of sentences explaining the experience (each sentence
        will be rendered as a HTML <li> element, unless there
        is only one sentence in which case we use <p>)
    """
    title:str
    items:List[str]


@dataclass(frozen=True)
class Experience:
    """
    Job, internship or study in my resume

    Parameters
    ----------
    title
        Title of the core skill e.g. "Data transformation"
    name
        Company or school name
    date_range
        Date range as a string e.g. "10.2014 – 04.2016"
    location
        E.g. city
    items
        List of sentences explaining the experience (each sentence
        will be rendered as a HTML <li> element, unless there
        is only one sentence in which case we use <p>)
    icon_name
        Name of the icon to use on the left of the `label`
        (see folder `static/icons`)
    """
    title:str
    name:str
    date_range:str
    location:str
    items:List[str]
    icon_name:Optional[str] = dataclassfield(default=None)


def get_extra_files(extra_dirs:List[str]) -> List[str]:
    """
    Gets a list of "extra" files to be monitored by flask and reloaded
    on changes when doing live development.
    See https://stackoverflow.com/a/9511655/10551772

    Examples
    --------
    >>> filepaths = get_extra_files(extra_dirs=['./static', './templates'])
    """
    extra_dirs = [extra_dirs] if isinstance(extra_dirs, str) else extra_dirs
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    return extra_files


# -

# # Data
#
# In the same order as it appears in the web page (from top to bottom or left to right if in the same container).

# ## Progress skills

# +
languages = [ProgressSkill(label='Französisch', progress=100, icon_name='FR.svg', label_bar='C2'),
             ProgressSkill(label='Englisch', progress=100, icon_name='GB.svg', label_bar='C1'),
             ProgressSkill(label='Deutsch', progress=90, icon_name='DE.svg', label_bar='C1'),
             ProgressSkill(label='Italienisch', progress=80, icon_name='IT.svg', label_bar='B2'),
             ProgressSkill(label='Russisch', progress=60, icon_name='RU.svg', label_bar='B1')]


programming_languages = [ProgressSkill(label='Python', progress=95, icon_name='python.png'),
                         ProgressSkill(label='SQL', progress=60, icon_name="postgresql.svg"),
                         ProgressSkill(label='Bash', progress=15, icon_name='bash.png'),
                         ProgressSkill(label='Java', progress=10, icon_name='java.png')]


tools = [ProgressSkill(label='Jupyter Lab', progress=90, icon_name='jupyterlab.png'),
         ProgressSkill(label='Tableau', progress=85, icon_name='tableau.png'),
         ProgressSkill(label='Excel', progress=60, icon_name='excel.png'),
         ProgressSkill(label='AWS', progress=25, icon_name='aws.png'),
         ProgressSkill(label='Docker', progress=10, icon_name='docker.png')]


markup_languages = [ProgressSkill(label='Markdown', progress=90, icon_name="markdown.png"),
                    ProgressSkill(label='HTML|CSS', progress=20, icon_name="html_css.png")]
# -

# ## Core skills

# +
data_wrangling = TextSkill(title='Datenverarbeitung in Python',
                           items=['<b>Tabellentransformierung</b> mit <a href="https://pandas.pydata.org/pandas-docs/stable/index.html">pandas</a>',
                                  '<b>SQL</b> Modellierung und Workflows mit <a href="https://www.sqlalchemy.org/">sqlalchemy</a>',
                                  'Mit vielen <b>verschiedenen Datenquellen</b> arbeiten (SQL, REST und SOAP API, Excel, CSV, ...)'])


library_dev = TextSkill(title='Entwicklung von Bibliotheken und Scripte',
                        items=['<b>Testing</b> mit <a href="https://docs.pytest.org/en/7.1.x/">pytest</a> (inkl. coverage und doctest)',
                               '<b>Dokumentation</b> (numpydoc guide style, GitHub Wiki)',
                               '<b>Maintenance</b> (Commits, Tags, Releases, Issues, PR,...)'])


data_viz = TextSkill(title='Datenvisualisierung',
                     items=['Gestaltung von <b>komplexen <a href="https://www.tableau.com/">Tableau</a> Dashboards</b> mit Hilfe von <b>Python</b> Scripte und '
                            'meistens <b>PostgreSQL</b> als "Brücke" für die Daten'])


webscraping = TextSkill(title='Webscraping',
                        items=['Automatische <b>Navigation und Datenextrahierung</b> auf Internetseiten '
                               'mit Tools wie <a href="https://playwright.dev/">Microsoft Playwright</a> und '
                               '<a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">BeautifulSoup</a>'])
# -

# ## Soft skills

soft_skills = [TextSkill(title='Softskills',
                         items=['Eigeninitiative',
                                'Zuverlässigkeit',
                                'Teamplayer und soziale Kompetenzen im Umgang mit verschiedenen Gesprächspartnern',
                                'Arbeitspraxis im internationalen Umfeld',
                                'Sehr gute schriftliche und mündliche Kommunikationsfähigkeit'])]

# ## Jobs

jobs = [Experience(title='Data Analyst',
                   name='port-neo GmbH',
                   date_range='Jan 2018 - jetzt',
                   location='Freiburg-im-Breisgau',
                   icon_name='port_neo_wx60.png',
                   items=['Erhebung, Verarbeitung und Export von <b>Marketingdaten</b> (aus Newsletterdaten, CRM, APIs, ...) und interne <b>Controllingdaten</b>',
                          '<b>Datenbereinigung</b> (Kodierung, Dubletten, Geodaten, Sonderzeichen, Namen, Firmennamen...) und <b>Datenanreicherung</b> (bspw. Geocodierung)',
                          'Entwicklung und Maintenance von <b>30+ Bibliotheken</b> mit der Sprache Python um u.a. die oben erwähnten Problemen zu lösen',
                          'Einrichtung von <b>automatischen Datenworkflows</b> mit der Hilfe von <b>AWS</b>, Docker, cron jobs oder systemd',
                          'Konzipierung von Marketing <b>Dashboards</b> mit Tableau (insb. Newsletter- und personenbezogenen Daten)']),
        Experience(title='Junior Online Marketing Manager (befristet)',
                   name='TANDEM Kommunikation GmbH',
                   date_range='06.2017 – 11.2017',
                   location='Freiburg-im-Breisgau',
                   icon_name='tandem_wx60.png',
                   items=['Installierung von Tools wie <b>Google Analytics</b> und Tag Manager um Website Daten zu erheben auf <b>25+ Websites</b>. '
                          'Automatische Erstellung von Berichten um diese Daten zu präsentieren (via Data Studio und API von Google Analytics)',
                          'Häufige Arbeit mit Daten von <b>AdWords</b> um Konten zu optimieren, teilweise mit Python']),
        Experience(title='Junior Account Manager Online Marketing (befristet)',
                   name='exito GmbH & Co. KG',
                   date_range='08.2016 – 12.2016',
                   location='Nürnberg',
                   icon_name='exito_wx60.png',
                   items=['Konzeption, Weiterentwicklung und Auswertung von französischen und italienischen Kundenkampagnen '
                          'mit dem Schwerpunkt <b>SEA</b> und Berichte für den Kunden',
                          'Erstellung von Anzeigentexten und Auswahl von Landing Pages sowie Keywords',
                          'Steuerung, Optimierung und Kontrollierung des <b>Budgets</b> von Kampagnen auf Basis von <b>Performancezielen</b>']),
        Experience(title='Projektmanager (befristet)',
                   name='Arbeit und Leben NRW',
                   date_range='05.2015 – 04.2016',
                   location='Düsseldorf',
                   icon_name='aulnrw_wx60.png',
                   items=['<b>Organisation</b> und <b>Begleitung</b> von <b>10 Begegnungen</b> zwischen <b>deutschen und französischen</b> Auszubildenden',
                          '<b>Leitung vor Ort</b> von einigen dieser Begegnungen und Ausbildung „interkultureller Jugendleiter“',
                          'Mitarbeit an der <b>Entwicklung von Partnerschaften</b> zwischen Arbeit und Leben NRW sowie berufsbildenden und/oder sozialpolitisch engagierten Einrichtungen'])]

# ## Studies

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
                      name='Université Paris Est Créteil (UPEC)', date_range='10. 2012 - 09. 2014', location='Créteil, Frankreich',
                      items=['Bericht „Qualität und Ausbildung“ als Vorbereitung auf ein '
                             'Praktikum beim Dialoge Sprachinstitut (Sept. 2013, 35 S. auf Französisch)']),
           Experience(title='Viersprachiger Bachelor of Arts „Internationaler Handel“', name='Université Paris Est Créteil (UPEC)',
                      date_range='10.2009 - 08.2012', location='Créteil, Frankreich', items=[]),
           Experience(title='Baccalauréat (Sciences de l’Ingénieur) = Abitur (Ingenieurwissenschaften)', name='Lycée d’Arsonval',
                      date_range='10.2009 - 08.2012', location='Saint Maur des Fossés, Frankreich', items=[])]

# ## Internships

internships = [Experience(title='Assistent der Schulleitung',
                          name='Dialoge Sprachinstitut GmbH, Master Praktikum',
                          date_range='09. 2013 – 01.2014',
                          location='Lindau',
                          items=['Kundenbetreuung und Marketing',
                                 'Wettbewerbsanalyse und Suche nach potenziellen Kunden',
                                 '<b>Qualitätsmanagement</b>: Datenverarbeitung und Erstellung von Dokumenten für die ISO 9001 Akkreditierung']),
               Experience(title='Assistent des Teams Insolvenzverwalterbetreuung',
                          name='HSBC Trinkaus & Burkhardt AG Firmenkunden Bereich, Bachelor Praktikum',
                          date_range='05.2012 – 08.2012',
                          location='Düsseldorf',
                          items=['Einblick in die Richtlinien der Eigenkapitalunterlegung, Insolvenzgeldfinanzierung und Treuhandkontenverwaltung',
                                 'Unterstützung des Teams “Insolvenzverwalterbetreuung” bei Treuhandkonteneröffnung und Terminkontrolle von Insolvenzverfahren',
                                 'Abfrage von neuen Insolvenzverfahren'])]

# ## Holiday jobs

holiday_jobs = [Experience(title='Assistent Back Office',
                           name='HSBC Business Banking',
                           date_range='08.2011',
                           location='Saint-Maur-des-Fossés, Frankreich',
                           items=['Hilfe bei der Vorbereitung den finanziellen Dokumenten im Rahmen von Ausschreibungen.']),
                Experience(title='Assistent Back Office',
                           name='Société Générale',
                           date_range='08.2010',
                           location='Sucy-en-Brie, Frankreich',
                           items=['Archivierung von Dokumenten, Kontenschließung und -Eröffnung und Überprüfung von Kundendaten.'])]

# ## Encoded email to avoid spam
#
# See http://hcard.geekhood.net/encode/

encoded_email = 't&#x68;&#x69;ba&#x75;l&#x74;&#x2E;&#98;etr&#x65;&#x6d;i&#101;&#x75;x&#x40;&#x67;&#x6D;ail&#46;&#x63;&#111;&#x6D;'

# # Create the App

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


# # Create hooks and routes

# +
@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}


@app.route('/')
def index():
    return render_template('index.html',
                           encoded_email=encoded_email,
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
                           internships=internships,
                           studies=studies,
                           holiday_jobs=holiday_jobs)


# -

# # Start the App

if __name__ == '__main__':
    # for development we are going to need debug for reloading
    # python code and data within it
    # add a debug flag for the CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # run the app
    app.run(debug=args.debug, extra_files=get_extra_files(['./templates', './static']))
