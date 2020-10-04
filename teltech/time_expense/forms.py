from datetime import date

from flask_wtf import FlaskForm
from wtforms import (DateField, FloatField, SelectField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, NumberRange, ValidationError


class TimeExpenseForm(FlaskForm):
    project_list = ['Clould Chile - Project A', 'Clould Spain - Project B', 'PRJ-CLD-2020'] 
    project = SelectField('Project', choices=project_list, default=1, validators=[DataRequired()])
    start_date = DateField('Start Date', format='%d/%m/%Y', default=date.today, validators=[DataRequired()])
    end_date = DateField('End Date', format='%d/%m/%Y', default=date.today, validators=[DataRequired()])    
    hours_worked = FloatField('Hours Worked (h)', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField("Description", validators=[DataRequired()], render_kw={"placeholder": "Description of the task"})
    submit = SubmitField("Save")

    def validate_start_date(self, start_date):
        if start_date.data > self.end_date.data:
            raise ValidationError("Start Date can't be greater than End Date")
