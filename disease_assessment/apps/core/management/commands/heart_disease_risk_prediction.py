from django_pandas.io import read_frame
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
# Django
from django.core.management.base import BaseCommand

from apps.api.models import Person, MedicalRecord


class Command(BaseCommand):
    help = 'Heart disease risk prediction'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Process started'))

        persons = Person.objects.filter(id__in=MedicalRecord.objects.values_list(
            'person_id').distinct()).order_by('id').values('id', 'age', 'gender', 'heart_disease_risk')
        medical_records = MedicalRecord.objects.order_by('person_id', '-row_number').distinct(
            'person_id').values('person_id', 'systolic_blood_pressure', 'diastolic_blood_pressure', 'heart_rate')

        # Init dataset
        df = pd.concat([read_frame(persons), read_frame(medical_records)], sort=False, axis=1)
        print(df)

        # Split into training data and test data
        X = df[['age', 'gender', 'person_id', 'systolic_blood_pressure', 'diastolic_blood_pressure', 'heart_rate']]
        y = df['heart_disease_risk']

        # Create training and testing vars, It’s usually around 80/20 or 70/30.
        X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        # Now we’ll fit the model on the training data
        model = RandomForestClassifier()
        model.fit(X_train, Y_train)

        # Make predictions on validation dataset
        # predictions = model.predict(X_test)

        # Pickle model
        pd.to_pickle(model, r'new_model.pickle')

        # Unpickle model
        model = pd.read_pickle(r'new_model.pickle')

        # Take input from user
        person_id = int(input("Enter person id: "))
        age = int(input("Enter age: "))
        gender = int(input("Enter gender: "))
        systolic_blood_pressure = int(input("Enter systolic blood pressure: "))
        diastolic_blood_pressure = int(input("Enter diastolic blood pressure: "))
        heart_rate = int(input("Enter heart rate: "))

        # input must be 2D array
        result = model.predict(
            [[age, gender, person_id, systolic_blood_pressure, diastolic_blood_pressure, heart_rate]])
        print(result)
