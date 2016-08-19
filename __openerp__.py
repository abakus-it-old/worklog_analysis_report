{
    'name': 'Worklog analysis report',
    'version': '9.0.1.0',
    'category': 'Project',
    'depends': ['hr_analytic_timesheet_improvements'],
    'description': 
    """
    Worklog analysis report
    
    This modules creates a report for worklogs.
    
    This module has been developed by Bernard DELHEZ, intern @ AbAKUS it-solutions.
    """,
    'data': [
        'wizard/worklog_analysis_report_view.xml',
        'report/worklog_analysis_report.xml',
    ],
    'installable': True,
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
}
