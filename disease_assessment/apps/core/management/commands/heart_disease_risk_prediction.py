import time
from datetime import date
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score, plot_roc_curve
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
# Django
from django.core.management.base import BaseCommand
from django_pandas.io import read_frame
from django.db.models import Q

from apps.api.models import Person, MedicalTest, EMRProperty


class Command(BaseCommand):
    help = 'Heart disease risk prediction'

    def handle(self, *args, **options):
        start_time = time.time()
        np.random.seed(1)

        self.stdout.write(self.style.SUCCESS('Process started'))

        persons = Person.objects.filter(
            Q(id__in=MedicalTest.objects.values_list('person_id').distinct('person_id')) & Q(
              id__in=EMRProperty.objects.values_list('person_id').distinct('person_id'))).distinct('id').order_by('id')

        last_medical_tests = MedicalTest.objects.filter(person_id__in=persons).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        last_emr_properties = EMRProperty.objects.filter(person_id__in=persons).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        df0 = read_frame(persons.filter(
            id__in=last_medical_tests.values_list('person_id')).order_by('id'))[['id', 'birthdate', 'sex']].set_index('id')
        df0.sort_values('id', ascending=True, inplace=True)

        today = date.today()
        df0['birthdate'] = pd.to_datetime(df0['birthdate'], format='%Y-%m-%d')
        df0['age'] = df0.apply(
            lambda x: today.year - x['birthdate'].year - ((today.month, today.day) < (x['birthdate'].month, x['birthdate'].day)), axis=1)
        df0['gender'] = df0.apply(lambda x: 1 if x['sex'] == 'М' else 0,  axis=1)

        tmp_df1 = read_frame(last_medical_tests)[['person', 'property_name', 'property_value']]
        tmp_df1['person'] = pd.to_numeric(tmp_df1['person'], errors='coerce')
        tmp_df1.sort_values('person', ascending=True, inplace=True)
        piv1 = pd.pivot_table(tmp_df1, values='property_value', index=['person'], columns=['property_name'], aggfunc=np.sum, fill_value=0)
        df1 = pd.DataFrame(piv1.to_records())

        tmp_df2 = read_frame(last_emr_properties)[['person', 'property_name', 'property_value']]
        tmp_df2['person'] = pd.to_numeric(tmp_df2['person'], errors='coerce')
        tmp_df2.sort_values('person', ascending=True, inplace=True)
        piv2 = pd.pivot_table(tmp_df2, values='property_value', index=['person'], columns=['property_name'], aggfunc=np.sum, fill_value=0)
        df2 = pd.DataFrame(piv2.to_records())

        # # Init total dataframe
        df = pd.concat([df1, df2], axis=1)
        df['id'] = df0.index
        df = df.reset_index().set_index('id')
        df['age'] = df0['age']
        df['gender'] = df0['gender']

        df = df[['холестерин', 'рост', 'масса тела', 'индекс массы тела', 'SYS на левой руке', 'DIA на левой руке',
                 'SYS на правой руке', 'DIA на правой руке',  'age', 'gender', 'плотность (удельный вес)', 'СОЭ',
                 'общий билирубин', 'NEUT (сегментоядерные нейтрофилы)', 'HGB (гемоглобин)', 'NEUT#', 'LYM (лимфоциты)',
                 'WBC (лейкоциты)', 'уровень АлАТ', 'уровень АсАТ', 'палочкоядерные нейтрофилы', 'MONO (моноциты)',
                 'EO (эозинофилы)', 'уробилин (количественно)', 'глюкоза (капиллярная кровь)', 'количество']]
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)

        # # Unpickle model
        model = pd.read_pickle(r'new_model.pickle')

        # # Make prediction
        df['heart_disease_risk'] = model.predict(df)

        # # Update persons data
        for i, heart_disease_risk in df['heart_disease_risk'].to_dict().items():
            Person.objects.filter(id=i).update(heart_disease_risk=heart_disease_risk)

        print("--- %s seconds ---" % (time.time() - start_time))
        print(df)
        # print(df.loc[df['heart_disease_risk'] == False])
