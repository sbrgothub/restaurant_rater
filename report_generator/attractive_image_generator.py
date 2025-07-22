# report_generator/attractive_image_generator.py (FINAL CLOUD VERSION)
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

# --- CONFIGURATION ---
# IMPORTANT: This MUST be the "External Database URL" from your Render.com PostgreSQL details page.
DATABASE_URL = "postgres://your_user:your_password@your_host:5432/your_database" # <-- PASTE YOUR RENDER DATABASE URL HERE

# This is where the output images will be saved locally on the cashier's PC.
OUTPUT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# --- AESTHETIC CONFIGURATION (No changes here) ---
PRIMARY_COLOR = "#0D47A1"
SECONDARY_COLOR = "#FFC107"
TEXT_COLOR = "#333333"
BACKGROUND_COLOR = "#f5f5f5"
BAR_COLORS = ['#4285F4', '#34A853', '#FBBC05']

def generate_images():
    """
    Connects to the cloud database, analyzes the data, and generates two attractive image files locally.
    """
    print("Connecting to cloud database to generate report images...")
    
    try:
        # Create a SQLAlchemy engine, which manages connections to the cloud database
        engine = create_engine(DATABASE_URL)
        
        # Use a single connection for all queries in this cycle
        with engine.connect() as conn:
            # --- IMAGE 1: FOOD REPORT (Querying the cloud database) ---
            food_df = pd.read_sql_query(
                text("SELECT name, total_stars, total_quantity, rating_count FROM foods WHERE rating_count > 0"),
                conn
            )
            
            # --- IMAGE 2: SERVICE CHART (Querying the cloud database) ---
            service_df = pd.read_sql_query(
                text("SELECT comfort_rating, service_rating, staff_rating FROM service_ratings"),
                conn
            )
            
    except Exception as e:
        print(f"❌ Error connecting to or querying the cloud database: {e}")
        # Stop this cycle if we can't get data
        return

    # --- IMAGE 1 GENERATION LOGIC (No changes needed, it just processes the DataFrame) ---
    if not food_df.empty:
        food_df['rating'] = (food_df['total_stars'] / food_df['rating_count']).round(1)
        top_foods = food_df.sort_values(by='rating', ascending=False).head(5)

        fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
        fig.patch.set_facecolor(BACKGROUND_COLOR)
        ax.axis('off')
        fig.suptitle("Our Customers' Favorite Dishes", fontsize=24, fontweight='bold', color=PRIMARY_COLOR)
        ax.set_title("Live stats from our feedback system", fontsize=14, color=TEXT_COLOR, pad=20)

        y_position = 0.75
        for index, row in top_foods.iterrows():
            ax.text(0.05, y_position, row['name'], fontsize=18, fontweight='bold', color=TEXT_COLOR, va='center')
            quantity_text = f"{int(row['total_quantity'])} units sold"
            ax.text(0.05, y_position - 0.06, quantity_text, fontsize=12, color=TEXT_COLOR, va='center')
            rating_text = f"★ {row['rating']}/5.0"
            ax.text(0.95, y_position, rating_text, fontsize=18, color=SECONDARY_COLOR, ha='right', va='center')
            y_position -= 0.20

        food_report_path = os.path.join(OUTPUT_FOLDER, "attractive_food_report.png")
        plt.savefig(food_report_path, bbox_inches='tight')
        plt.close()
        print(f"✅ Attractive food report saved to: {food_report_path}")

    # --- IMAGE 2 GENERATION LOGIC (No changes needed, it just processes the DataFrame) ---
    if not service_df.empty:
        avg_ratings = {
            'Restaurant Comfort': service_df['comfort_rating'].mean(),
            'Service Provided': service_df['service_rating'].mean(),
            'Staff Character': service_df['staff_rating'].mean()
        }
        avg_df = pd.DataFrame.from_dict(avg_ratings, orient='index', columns=['Average Rating'])
        fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
        fig.patch.set_facecolor(BACKGROUND_COLOR)
        bars = ax.bar(avg_df.index, avg_df['Average Rating'], color=BAR_COLORS)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        ax.set_facecolor(BACKGROUND_COLOR)
        ax.tick_params(left=False, labelleft=False, bottom=False)
        ax.yaxis.grid(False)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f'{yval:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold', color=TEXT_COLOR)
        ax.set_title("How We're Doing", fontsize=24, fontweight='bold', color=PRIMARY_COLOR, pad=20)
        plt.xticks(fontsize=12, color=TEXT_COLOR)
        plt.ylim(0, 5)
        service_report_path = os.path.join(OUTPUT_FOLDER, "attractive_service_report.png")
        plt.savefig(service_report_path, bbox_inches='tight')
        plt.close()
        print(f"✅ Attractive service report saved to: {service_report_path}")

# --- THE INFINITE LOOP ---
if __name__ == "__main__":
    print("--- Starting Automated ATTRACTIVE Image Generator (Cloud Mode) ---")
    print("This script will generate new report images every 3 minutes.")
    print("Press Ctrl+C to stop.")
    
    while True:
        print("\n--- Running job cycle ---")
        generate_images()
        print(f"--- Job cycle complete. Sleeping for 3 minutes... ---")
        time.sleep(3 * 60)