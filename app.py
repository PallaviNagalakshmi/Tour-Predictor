from flask import Flask, render_template, request
import pandas as pd
import joblib
import pycountry
import plotly.express as px

app = Flask(__name__)

# Load model and data
model = joblib.load("best_model.pkl")
df = pd.read_csv("cleaned_data.csv")

# Filter out unwanted region rows
df = df[~df["Region"].isin(["Grand Total", "Not Classified elsewhere"])]

# Get updated unique values
countries = sorted(df["Country of Nationality"].unique())
regions = sorted([r for r in df["Region"].unique() if r not in ["Grand Total", "Not Classified Elsewhere"]])

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    prediction = None
    selected_country = ""
    selected_year = ""
    tourist_sources = []

    if request.method == "POST":
        selected_country = request.form["country"]
        selected_year = int(request.form["year"])

        country_row = df[df["Country of Nationality"] == selected_country]
        if not country_row.empty and 2021 <= selected_year <= 2025:
            arrivals = [
                country_row["Number of Arrivals-2017"].values[0],
                country_row["Number of Arrivals-2018"].values[0],
                country_row["Number of Arrivals-2019"].values[0],
                country_row["Number of Arrivals-2020"].values[0]
            ]
            current_arrivals = arrivals.copy()
            for y in range(2021, selected_year + 1):
                pred = model.predict([current_arrivals[-4:]])[0]
                current_arrivals.append(pred)
            prediction = int(current_arrivals[-1])
        else:
            prediction = "Data not found or year out of range."

        tourist_sources = df[df["Region"] == selected_country][
            ["Country of Nationality", "Number of Arrivals-2021"]
        ].sort_values(by="Number of Arrivals-2021", ascending=False).head(10).values.tolist()

    return render_template("prediction.html",
                           prediction=prediction,
                           countries=countries,
                           selected_country=selected_country,
                           selected_year=selected_year,
                           tourist_sources=tourist_sources)

@app.route("/trend", methods=["GET", "POST"])
def trend():
    single_prediction = None
    selected_country = None
    compare_predictions = []
    selected_compare = []

    years = [2017, 2018, 2019, 2020, 2021]
    pred_years = [2022, 2023, 2024, 2025]
    all_years = years + pred_years

    if request.method == "POST":
        if "country" in request.form:
            selected_country = request.form["country"]
            country_row = df[df["Country of Nationality"] == selected_country]

            if not country_row.empty:
                values = [int(country_row[f"Number of Arrivals-{y}"].values[0]) for y in years]
                arrivals = values[-4:]
                for _ in pred_years:
                    pred = model.predict([arrivals[-4:]])[0]
                    arrivals.append(pred)
                values += arrivals[4:]
                single_prediction = {
                    "country": selected_country,
                    "years": all_years,
                    "values": [int(v) for v in values],
                    "zipped": list(zip(all_years, [int(v) for v in values]))
                }

        elif "compare1" in request.form and "compare2" in request.form:
            selected_compare = [request.form["compare1"], request.form["compare2"]]

            for c in selected_compare:
                row = df[df["Country of Nationality"] == c]
                if not row.empty:
                    values = [int(row[f"Number of Arrivals-{y}"].values[0]) for y in years]
                    arrivals = values[-4:]
                    for _ in pred_years:
                        pred = model.predict([arrivals[-4:]])[0]
                        arrivals.append(pred)
                    values += arrivals[4:]
                    compare_predictions.append({
                        "country": c,
                        "years": all_years,
                        "values": [int(v) for v in values],
                        "zipped": list(zip(all_years, [int(v) for v in values]))
                    })

    return render_template("trend.html",
                           countries=countries,
                           prediction=single_prediction,
                           selected_country=selected_country,
                           compare_predictions=compare_predictions,
                           selected_compare=selected_compare)

@app.route("/growth")
def growth():
    growth_data = []

    for country in countries:
        row = df[df["Country of Nationality"] == country]
        if not row.empty:
            try:
                arrivals = [
                    row["Number of Arrivals-2018"].values[0],
                    row["Number of Arrivals-2019"].values[0],
                    row["Number of Arrivals-2020"].values[0],
                    row["Number of Arrivals-2021"].values[0]
                ]
                predicted = arrivals.copy()
                for _ in range(2022, 2026):
                    next_pred = model.predict([predicted[-4:]])[0]
                    predicted.append(next_pred)
                growth = predicted[-1] - arrivals[-1]
                growth_data.append({
                    "country": country,
                    "from_2021": int(arrivals[-1]),
                    "to_2025": int(predicted[-1]),
                    "growth": int(growth)
                })
            except Exception:
                continue

    top5 = sorted(growth_data, key=lambda x: x["growth"], reverse=True)[:5]
    return render_template("growth.html", top5=top5)

@app.route("/region", methods=["GET", "POST"])
def region():
    selected_year = None
    region_data = {}

    if request.method == "POST":
        selected_year = int(request.form["year"])
        if selected_year < 2022 or selected_year > 2025:
            return render_template("region.html",
                                   error="Please select a year between 2022 and 2025.",
                                   regions=regions,
                                   selected_year=selected_year,
                                   region_data=None)

        for country in countries:
            row = df[df["Country of Nationality"] == country]
            if not row.empty:
                try:
                    region = row["Region"].values[0]
                    if region in ["Grand Total", "Not Classified Elsewhere"]:
                        continue
                    arrivals = [
                        row["Number of Arrivals-2018"].values[0],
                        row["Number of Arrivals-2019"].values[0],
                        row["Number of Arrivals-2020"].values[0],
                        row["Number of Arrivals-2021"].values[0],
                    ]
                    current_arrivals = arrivals.copy()
                    for y in range(2022, selected_year + 1):
                        pred = model.predict([current_arrivals[-4:]])[0]
                        current_arrivals.append(pred)
                    final_prediction = current_arrivals[-1]
                    if region not in region_data:
                        region_data[region] = 0
                    region_data[region] += final_prediction
                except Exception:
                    continue

    return render_template("region.html",
                           selected_year=selected_year,
                           regions=sorted(region_data.keys()),
                           region_data=region_data)

@app.route("/worldmap")
def worldmap():
    data = []

    for country in countries:
        row = df[df["Country of Nationality"] == country]
        if not row.empty:
            try:
                arrivals = [
                    row["Number of Arrivals-2018"].values[0],
                    row["Number of Arrivals-2019"].values[0],
                    row["Number of Arrivals-2020"].values[0],
                    row["Number of Arrivals-2021"].values[0]
                ]
                for _ in range(2022, 2026):
                    pred = model.predict([arrivals[-4:]])[0]
                    arrivals.append(pred)
                predicted_2025 = arrivals[-1]
                iso_code = get_country_code(country)
                if iso_code:
                    data.append({
                        "country": country,
                        "iso_code": iso_code,
                        "tourists": int(predicted_2025)
                    })
            except Exception:
                continue

    df_map = pd.DataFrame(data)
    fig = px.choropleth(df_map,
                        locations="iso_code",
                        color="tourists",
                        hover_name="country",
                        color_continuous_scale="Blues",
                        projection="natural earth",
                        title="")
    map_html = fig.to_html(full_html=False)
    return render_template("worldmap.html", map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
