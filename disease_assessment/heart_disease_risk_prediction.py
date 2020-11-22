from django_pandas.io import read_frame
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from apps.api.models import Person, MedicalRecord
from django.conf import settings


settings.configure()
persons = Person.objects.filter(id__in=MedicalRecord.objects.values_list('person_id').distinct())
medical_records = MedicalRecord.objects.all()

medical_records.union(persons)

# Init dataset
df = read_frame(medical_records)

# Split into training data and test data
X = df[['person_id', 'birthdate', 'sex', 'blood_pressure', 'heart_rate']]
y = df['heart_disease_risk']

# Create training and testing vars, It’s usually around 80/20 or 70/30.
X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Now we’ll fit the model on the training data
model = RandomForestClassifier()
model.fit(X_train, Y_train)

# Make predictions on validation dataset
predictions = model.predict(X_test)


# Pickle model
pd.to_pickle(model, r'new_model.pickle')

# Unpickle model
model = pd.read_pickle(r'new_model.pickle')

# Take input from user
person_id = int(input("Enter person id: "))
birthdate = input("Enter birthdate: ")
sex = input("Enter gender: ")
blood_pressure = input("Enter blood pressure: ")
heart_rate = int(input("Enter heart rate: "))

result = model.predict([[person_id, birthdate, sex, blood_pressure, heart_rate]])  # input must be 2D array
print(result)
