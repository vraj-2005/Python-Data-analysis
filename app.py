from flask import Flask, render_template, request
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load model & scaler
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get values from form in the expected order (matching trained model features)
        input_fields = [
            'screen', 'social', 'gaming', 'work',
            'sleep', 'notif', 'opens', 'weekend'
        ]

        values = []
        for f in input_fields:
            val_str = request.form.get(f, '0')
            try:
                val = float(val_str)
                values.append(val)
            except ValueError:
                all_fields = [
                    'age', 'screen', 'social', 'gaming', 'work',
                    'sleep', 'notif', 'opens', 'weekend'
                ]
                form_values = {f: request.form.get(f, '') for f in all_fields}
                return render_template('index.html', prediction_text=f"Please enter a valid number for {f.replace('_', ' ').title()}.", **form_values)

        final_input = np.array([values])

        prediction = model.predict(final_input)
        print("Values:", values)
        print("Prediction:", prediction)
        result = "Yes" if int(prediction[0]) == 1 else "No"

        if result == "Yes":
            prediction_text = "⚠️ User is Addicted to Smartphone"
        else:
            prediction_text = "✅ User is Not Addicted"

        # Store the prediction and age
        age_value = request.form.get('age', '21')
        with open('predictions_log.txt', 'a') as f:
            f.write(f"Age: {age_value}, Prediction: {result}\n")

        # Preserve all form values
        all_fields = [
            'age', 'screen', 'social', 'gaming', 'work',
            'sleep', 'notif', 'opens', 'weekend'
        ]
        form_values = {f: request.form.get(f, '') for f in all_fields}

        # Build summary data for UI display
        summary = {
            'Age': form_values.get('age', '21'),
            'Daily Screen Time (hours)': form_values.get('screen', '7.5'),
            'Social Media Hours': form_values.get('social', '5'),
            'Gaming Hours': form_values.get('gaming', '5'),
            'Work/Study Hours': form_values.get('work', '6'),
            'Sleep Hours': form_values.get('sleep', '6'),
            'Notifications Per Day': form_values.get('notif', '250'),
            'App Opens Per Day': form_values.get('opens', '150'),
            'Weekend Screen Time': form_values.get('weekend', '7.5')
        }

        return render_template('index.html', prediction_text=prediction_text, result_label='Addicted' if result == 'Yes' else 'Not Addicted', summary=summary, **form_values)

    except Exception as e:
        print('Prediction error:', e)
        # Preserve form values even on error
        all_fields = [
            'age', 'screen', 'social', 'gaming', 'work',
            'sleep', 'notif', 'opens', 'weekend'
        ]
        form_values = {f: request.form.get(f, '') for f in all_fields}
        return render_template('index.html', prediction_text=str(e), **form_values)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    