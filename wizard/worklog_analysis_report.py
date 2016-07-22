from openerp import models, fields, api, _
import datetime
import logging
import pytz
_logger = logging.getLogger(__name__)

class worklog_analysis_report(models.TransientModel):
    _name = "worklog.analysis.report"
    user_id = fields.Many2one('res.users',string="User")
    date_start = fields.Date('Start Date')
    date_stop = fields.Date('End Date')
    
    def get_report(self, cr, uid, ids, context=None):
        return self.pool.get('report').get_action(cr, uid, ids[0], 'worklog_analysis_report.worklog_analysis_report', context=context)

    def get_report_data(self):
        cr = self.env.cr
        uid = self.env.user.id
        
        search_query = []
        if self.user_id:
            hr_analytic_timesheet_obj = self.pool.get('account.analytic.line')
            
            search_query.append(tuple(['user_id', '=', self.user_id.id]))
            if self.date_start:
                search_query.append(tuple(['date', '>=', self.date_start]))
            if self.date_stop:
                search_query.append(tuple(['date', '<=', self.date_stop]))
            timesheet_ids = hr_analytic_timesheet_obj.search(cr, uid, search_query)
            
            data = {}
            data['WEEKS'] = []
            data['TOTAL'] = 0
            data['EMPLOYEE'] = self.user_id.name
            
            #Define the period
            if self.date_start:
                start_date = datetime.datetime.strptime(self.date_start, "%Y-%m-%d").date().strftime('%d-%m-%Y')
            else:
                start_date = "Past"
            
            if self.date_stop:
                end_date = datetime.datetime.strptime(self.date_stop, "%Y-%m-%d").date().strftime('%d-%m-%Y')
            else:
                end_date = "Now"

            week_numbers_dict = {}
            days_dict = {}
            
            local_tz = pytz.timezone(self.env.user.tz)

            # Browse account.analytic.lines
            for line in hr_analytic_timesheet_obj.browse(cr, uid, timesheet_ids):
                date_begin_datetime_obj = pytz.utc.localize(datetime.datetime.strptime(line.date_begin, '%Y-%m-%d %H:%M:%S')).astimezone(local_tz)
                date_begin_date_obj = date_begin_datetime_obj.date()

                date_begin_string = date_begin_date_obj.strftime('%d-%m-%Y')
                
                week_number = date_begin_date_obj.isocalendar()[1]
                day_number = date_begin_datetime_obj.weekday()
                day_date = date_begin_datetime_obj.strftime('%d-%m-%Y %H:%M:%S')
                contract_name = line.account_id.name
                duration = line.unit_amount
                description = line.name
                
                if week_number in week_numbers_dict:
                    week = week_numbers_dict[week_number]
                    week["TOTAL"] = week["TOTAL"]+duration
                    data['TOTAL'] = data['TOTAL']+duration
                    if date_begin_string in days_dict:
                        day = days_dict[date_begin_string]
                        day["TOTAL"] = day["TOTAL"]+duration
                        day["DATA"].append({"DATE": day_date, "CONTRACT_NAME": contract_name, "DURATION": duration, "DESCRIPTION": description})
                    else:
                        day = {"DAY_NUMBER": day_number,"DATE": date_begin_string, "TOTAL": duration, "DATA": [{"DATE": day_date, "CONTRACT_NAME": contract_name, "DURATION": duration, "DESCRIPTION": description}]}
                        week["DAYS"].append(day)
                        days_dict[date_begin_string] = day
                    
                else:
                    day = {"DAY_NUMBER": day_number,"DATE": date_begin_string, "TOTAL": duration, "DATA": [{"DATE": day_date, "CONTRACT_NAME": contract_name, "DURATION": duration, "DESCRIPTION": description}]}
                    days = []
                    days.append(day)
                    days_dict[date_begin_string] = day
                    
                    week = {"WEEK_NUMBER": week_number, "DAYS": days, "TOTAL": duration}
                    week_numbers_dict[week_number] = week
                    
                    data['TOTAL'] = data['TOTAL']+duration
                    data["WEEKS"].append(week)

            #sort weeks
            data["WEEKS"] = sorted(data["WEEKS"], key=lambda k: k['WEEK_NUMBER'])

            for week in data["WEEKS"]:
                #sort days
                week["DAYS"] = sorted(week["DAYS"], key=lambda k: k['DAY_NUMBER'])
                for day in week["DAYS"]:
                    #sort day data
                    day["DATA"] = sorted(day["DATA"], key=lambda k: k['DATE'])

            if start_date == "Past":
                start_date = data["WEEKS"][0]["DAYS"][0]["DATE"]

            if end_date == "Now":
                days = data["WEEKS"][len(data["WEEKS"])-1]["DAYS"]
                end_date = days[len(days)-1]["DATE"]

            data['PERIOD'] = start_date + " - " + end_date
            
            return data
        return False
        
    def format_decimal_number(self, number, point_numbers=2, separator=','):
        number_string = str(round(round(number, point_numbers+1),point_numbers))
        for x in range(0, point_numbers):
            if len(number_string[number_string.rfind('.')+1:]) < 2:
                number_string += '0'
            else:
                break        
        return number_string.replace('.',separator)
        
    def decimal_to_hours(self, hoursDecimal):
        hours = int(hoursDecimal);
        minutesDecimal = ((hoursDecimal - hours) * 60);
        minutes = int(minutesDecimal);
        if minutes<10:
            minutes = "0"+str(minutes)
        else:
            minutes = str(minutes)
        hours = str(hours)
        return hours + ":" + minutes
