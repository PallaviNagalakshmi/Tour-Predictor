# 🧳 Tour Predictor

This project is a **Tourism Prediction and Analysis Web Application** that helps visualize tourism trends and predict the number of tourists visiting different regions using historical data and machine learning models. The system is designed to support tourism boards, analysts, and researchers in understanding patterns and planning effectively.

## 🚀 Features

- 📈 **Tourism Growth Analysis**: Interactive charts and visualizations show how tourism evolved over time.
- 🌍 **Regional and National Trends**: Separate dashboards for region-wise statistics and national-level trends.
- 🤖 **Tourist Prediction**: Predict the number of tourists based on user input using a trained machine learning model.
- 🗺️ **World Map View**: Visualizes global tourism contribution to India.

## 🧠 Technologies Used

- Python
- Flask (Backend)
- HTML, CSS (Frontend)
- Pandas, NumPy (Data Handling)
- scikit-learn (Machine Learning)
- Matplotlib, Seaborn (Visualization)
- Jupyter Notebook (Model Development)

## 📁 Project Structure
```plain text
Tourism/
├── app.py
├── best_model.pkl
├── cleaned_data.csv
├── India-Tourism-Statistics-2022-Table-2.1.4.csv
├── Tourist_prediction.ipynb
├── static/
│   └── tourism_bg.png
├── templates/
   ├── index.html
   ├── prediction.html
   ├── region.html
   ├── growth.html
   ├── trend.html
   └── worldmap.html
```

## 🔧 How to Run

  ### 1. Clone the repository
  ```bash
  git clone https://github.com/your-username/Tour-Predictor.git
  cd Tour-Predictor/Tourism
  ```
  ### 2. Create a virtual environment (optional but recommended)
  ```bash
  python -m venv venv
  ```
  ### 3. Activate the environment
  On Windows:
  ```bash
  venv\Scripts\activate
  ```
  On macOS/Linux:
  
  ```bash
  source venv/bin/activate
  ```
  ### 4. Install required packages
  ```bash
  pip install -r requirements.txt
  ```
  ### 5. Run the Flask App
  ```bash
  python app.py
  ```
