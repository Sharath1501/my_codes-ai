import pandas as pd
df = pd.read_csv("dark-patterns.csv")

df = df.drop_duplicates()
df = df.dropna()

print("Cleaned Dataset:")
print(df.head())

df.to_csv('cleaned_dataset.csv', index=False)
from sklearn.model_selection import train_test_split

from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
df = pd.read_csv('cleaned_dataset.csv')
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
X_text = tfidf_vectorizer.fit_transform(df['Pattern String'])
X_categorical = pd.get_dummies(df[['Pattern Category', 'Pattern Type', 'Where in website?']])
from scipy.sparse import hstack
X = hstack([X_text, X_categorical]).toarray()
y = df['Deceptive?']

print("Training set shape:", X_train.shape)
print("Testing set shape:", X_test.shape)

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

report = classification_report(y_test, y_pred)
print("Accuracy:", accuracy)
print("Classification Report:\n", report)
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)
print("Confusion Matrix:\n", conf_matrix)


sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()
