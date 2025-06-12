import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

# File paths
train_path = r"C:\Users\shiva\Downloads\Code\Projects\anti-ddos-ml\ml\data\archive\UNSW_NB15_training-set.csv"
test_path = r"C:\Users\shiva\Downloads\Code\Projects\anti-ddos-ml\ml\data\archive\UNSW_NB15_testing-set.csv"


print("Loading datasets...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

print(f"Training data shape: {train_df.shape}")
print(f"Testing data shape: {test_df.shape}")

# Target column
label_col = 'label'

# Drop irrelevant columns if present
drop_cols = ['id', 'attack_cat']
train_df.drop(columns=[col for col in drop_cols if col in train_df.columns], inplace=True)
test_df.drop(columns=[col for col in drop_cols if col in test_df.columns], inplace=True)

# Ensure 'label' column exists
if label_col not in train_df.columns or label_col not in test_df.columns:
    raise ValueError(f"'{label_col}' column not found in either train or test set!")

print("Available columns in training set:")
print(list(train_df.columns))

# Encode target
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(train_df[label_col])
y_test = label_encoder.transform(test_df[label_col])
X_train = train_df.drop(columns=[label_col])
X_test = test_df.drop(columns=[label_col])

# Handle categorical features
cat_cols = X_train.select_dtypes(include=['object']).columns
print(f"Categorical columns to encode: {list(cat_cols)}")

encoders = {}
for col in cat_cols:
    enc = LabelEncoder()
    # Add "unknown" category to training if not already present
    if 'unknown' not in X_train[col].values:
        X_train[col] = X_train[col].fillna('unknown')
        enc.fit(list(X_train[col].unique()) + ['unknown'])  # ensure 'unknown' in classes
    else:
        enc.fit(X_train[col])
    
    X_train[col] = enc.transform(X_train[col])
    
    # Replace unknowns in test set
    X_test[col] = X_test[col].apply(lambda x: x if x in enc.classes_ else 'unknown')
    enc_classes = list(enc.classes_)
    if 'unknown' not in enc_classes:
        enc_classes.append('unknown')
        enc.classes_ = enc_classes
    X_test[col] = enc.transform(X_test[col])
    
    encoders[col] = enc

print(f"Training features shape: {X_train.shape}, labels shape: {y_train.shape}")

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Report
target_names = [str(cls) for cls in label_encoder.classes_]
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))

# Save everything
joblib.dump(clf, 'unsw_nb15_rf_model.pkl')
joblib.dump(label_encoder, 'unsw_nb15_label_encoder.pkl')
joblib.dump(encoders, 'unsw_nb15_feature_encoders.pkl')

print("Model, label encoder, and feature encoders saved.")
