#!/usr/bin/env python3
"""
Delhi NCR Air Quality Data Analysis Script

This script retrieves historical air quality data for Delhi NCR districts
using the OpenAQ API and generates a comprehensive CSV report.

Requirements:
- openaq library
- pandas
- geopandas
- shapely
- requests

Install with: pip install openaq pandas geopandas shapely requests
"""

import openaq
import pandas as pd
import geopandas as gpd
import json
from datetime import datetime, timedelta
import time
import logging
from shapely.geometry import Point
from typing import List, Dict, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DelhiNCRAirQualityAnalyzer:
    """
    A class to analyze air quality data for Delhi NCR region using OpenAQ API
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the analyzer with OpenAQ client
        
        Args:
            api_key: OpenAQ API key (optional but recommended for higher rate limits)
        """
        self.api_key = api_key or "3ca52f4c7c29ca4728b1e2bf7d6bcb3ec0971bb9a972225e2666fe0a8db66243"
        self.client = openaq.OpenAQ(api_key=self.api_key)
        self.geojson_path = "Delhi_NCR_Districts.geojson"
        self.districts_gdf = None
        self.locations_data = []
        
    def load_district_boundaries(self) -> bool:
        """
        Load district boundaries from GeoJSON file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.geojson_path):
                logger.error(f"GeoJSON file not found: {self.geojson_path}")
                return False
                
            self.districts_gdf = gpd.read_file(self.geojson_path)
            logger.info(f"Loaded {len(self.districts_gdf)} districts from GeoJSON")
            
            # Display district information
            logger.info("Districts loaded:")
            for idx, row in self.districts_gdf.iterrows():
                logger.info(f"  - {row['NAME_2']} ({row['NAME_1']})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading district boundaries: {e}")
            return False
    
    def get_monitoring_locations(self) -> List[Dict]:
        """
        Retrieve all monitoring locations in Delhi NCR region
        
        Returns:
            List of location dictionaries
        """
        try:
            # Delhi NCR center coordinates with 50km radius to cover all districts
            lat, lon = 28.6139, 77.2090
            radius = 50000  # 50km in meters
            
            logger.info(f"Fetching monitoring locations within {radius/1000}km of Delhi NCR center...")
            
            # Get locations using OpenAQ v3 API
            locations = self.client.locations.get(
                coordinates=f"{lat},{lon}",
                radius=radius,
                limit=1000
            )
            
            self.locations_data = locations.get('results', [])
            logger.info(f"Found {len(self.locations_data)} monitoring locations")
            
            return self.locations_data
            
        except Exception as e:
            logger.error(f"Error fetching monitoring locations: {e}")
            return []
    
    def assign_districts_to_locations(self) -> pd.DataFrame:
        """
        Assign each monitoring location to its corresponding district
        
        Returns:
            DataFrame with locations and their assigned districts
        """
        if not self.locations_data or self.districts_gdf is None:
            logger.error("No location data or district boundaries available")
            return pd.DataFrame()
        
        location_district_map = []
        
        for location in self.locations_data:
            try:
                lat = location.get('coordinates', {}).get('latitude')
                lon = location.get('coordinates', {}).get('longitude')
                
                if lat is None or lon is None:
                    continue
                
                point = Point(lon, lat)
                
                # Find which district contains this point
                assigned_district = None
                assigned_state = None
                
                for idx, district_row in self.districts_gdf.iterrows():
                    if district_row.geometry.contains(point):
                        assigned_district = district_row['NAME_2']
                        assigned_state = district_row['NAME_1']
                        break
                
                # If not found in any district, assign to nearest one
                if assigned_district is None:
                    distances = self.districts_gdf.geometry.distance(point)
                    nearest_idx = distances.idxmin()
                    assigned_district = self.districts_gdf.loc[nearest_idx, 'NAME_2']
                    assigned_state = self.districts_gdf.loc[nearest_idx, 'NAME_1']
                    logger.warning(f"Location {location.get('name', 'Unknown')} assigned to nearest district: {assigned_district}")
                
                location_district_map.append({
                    'location_id': location.get('id'),
                    'location_name': location.get('name', 'Unknown'),
                    'latitude': lat,
                    'longitude': lon,
                    'district': assigned_district,
                    'state': assigned_state,
                    'city': location.get('city', 'Unknown'),
                    'country': location.get('country', 'Unknown'),
                    'parameters': [param.get('parameter') for param in location.get('parameters', [])],
                    'sensors_count': len(location.get('sensors', [])),
                    'first_updated': location.get('firstUpdated'),
                    'last_updated': location.get('lastUpdated')
                })
                
            except Exception as e:
                logger.warning(f"Error processing location {location.get('id', 'Unknown')}: {e}")
                continue
        
        df = pd.DataFrame(location_district_map)
        logger.info(f"Successfully assigned {len(df)} locations to districts")
        
        # Display district assignment summary
        if not df.empty:
            district_summary = df.groupby(['state', 'district']).size().reset_index(name='location_count')
            logger.info("District assignment summary:")
            for _, row in district_summary.iterrows():
                logger.info(f"  {row['state']} - {row['district']}: {row['location_count']} locations")
        
        return df
    
    def get_measurements_for_locations(self, location_df: pd.DataFrame, 
                                     days_back: int = 30,
                                     parameters: List[str] = None) -> pd.DataFrame:
        """
        Retrieve measurements for all locations
        
        Args:
            location_df: DataFrame with location information
            days_back: Number of days back to fetch data
            parameters: List of parameters to fetch (default: common pollutants)
            
        Returns:
            DataFrame with measurements
        """
        if parameters is None:
            parameters = ['pm25', 'pm10', 'no2', 'so2', 'o3', 'co']
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        all_measurements = []
        
        for idx, location in location_df.iterrows():
            location_id = location['location_id']
            
            try:
                logger.info(f"Fetching measurements for {location['location_name']} ({location['district']})")
                
                # Get measurements for this location
                measurements = self.client.measurements.get(
                    locations_id=location_id,
                    date_from=start_date.strftime('%Y-%m-%d'),
                    date_to=end_date.strftime('%Y-%m-%d'),
                    parameters=parameters,
                    limit=10000
                )
                
                results = measurements.get('results', [])
                logger.info(f"  Retrieved {len(results)} measurements")
                
                for measurement in results:
                    all_measurements.append({
                        'location_id': location_id,
                        'location_name': location['location_name'],
                        'district': location['district'],
                        'state': location['state'],
                        'city': location['city'],
                        'latitude': location['latitude'],
                        'longitude': location['longitude'],
                        'parameter': measurement.get('parameter'),
                        'value': measurement.get('value'),
                        'unit': measurement.get('unit'),
                        'date': measurement.get('date', {}).get('utc'),
                        'coordinates': measurement.get('coordinates')
                    })
                
                # Rate limiting to avoid API limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error fetching measurements for location {location_id}: {e}")
                continue
        
        measurements_df = pd.DataFrame(all_measurements)
        
        if not measurements_df.empty:
            # Convert date column to datetime
            measurements_df['date'] = pd.to_datetime(measurements_df['date'])
            measurements_df['date_local'] = measurements_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"Total measurements retrieved: {len(measurements_df)}")
            
            # Display summary by parameter and district
            if len(measurements_df) > 0:
                summary = measurements_df.groupby(['district', 'parameter']).agg({
                    'value': ['count', 'mean', 'min', 'max'],
                    'location_name': 'nunique'
                }).round(2)
                
                summary.columns = ['measurement_count', 'avg_value', 'min_value', 'max_value', 'location_count']
                summary = summary.reset_index()
                
                logger.info("Measurement summary by district and parameter:")
                for _, row in summary.head(20).iterrows():  # Show first 20 rows
                    logger.info(f"  {row['district']} - {row['parameter']}: "
                              f"{row['measurement_count']} measurements, "
                              f"avg: {row['avg_value']}, "
                              f"locations: {row['location_count']}")
        
        return measurements_df
    
    def generate_district_summary(self, measurements_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate district-wise summary statistics
        
        Args:
            measurements_df: DataFrame with all measurements
            
        Returns:
            DataFrame with district summary
        """
        if measurements_df.empty:
            return pd.DataFrame()
        
        # Group by district and parameter to calculate statistics
        district_summary = measurements_df.groupby(['state', 'district', 'parameter']).agg({
            'value': ['count', 'mean', 'median', 'std', 'min', 'max'],
            'location_name': 'nunique',
            'date': ['min', 'max']
        }).round(2)
        
        # Flatten column names
        district_summary.columns = [
            'measurement_count', 'avg_value', 'median_value', 'std_value', 
            'min_value', 'max_value', 'location_count', 'date_from', 'date_to'
        ]
        
        district_summary = district_summary.reset_index()
        
        # Add data quality indicators
        district_summary['data_completeness'] = (
            district_summary['measurement_count'] / 
            (district_summary['location_count'] * 24 * 30)  # Assuming 30 days, 24 hours
        ).round(3)
        
        return district_summary
    
    def save_to_csv(self, location_df: pd.DataFrame, measurements_df: pd.DataFrame, 
                   district_summary_df: pd.DataFrame) -> bool:
        """
        Save all data to CSV files
        
        Args:
            location_df: DataFrame with location information
            measurements_df: DataFrame with all measurements
            district_summary_df: DataFrame with district summary
            
        Returns:
            bool: True if successful
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save locations data
            locations_file = f'delhi_ncr_locations_{timestamp}.csv'
            location_df.to_csv(locations_file, index=False)
            logger.info(f"Locations data saved to: {locations_file}")
            
            # Save measurements data
            if not measurements_df.empty:
                measurements_file = f'delhi_ncr_measurements_{timestamp}.csv'
                measurements_df.to_csv(measurements_file, index=False)
                logger.info(f"Measurements data saved to: {measurements_file}")
            
            # Save district summary
            if not district_summary_df.empty:
                summary_file = f'delhi_ncr_district_summary_{timestamp}.csv'
                district_summary_df.to_csv(summary_file, index=False)
                logger.info(f"District summary saved to: {summary_file}")
            
            # Save a comprehensive report
            self.generate_report(location_df, measurements_df, district_summary_df, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV files: {e}")
            return False
    
    def generate_report(self, location_df: pd.DataFrame, measurements_df: pd.DataFrame,
                       district_summary_df: pd.DataFrame, timestamp: str):
        """
        Generate a comprehensive text report
        """
        report_file = f'delhi_ncr_air_quality_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("Delhi NCR Air Quality Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Locations summary
            f.write("MONITORING LOCATIONS SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total monitoring locations: {len(location_df)}\n\n")
            
            if not location_df.empty:
                district_counts = location_df.groupby(['state', 'district']).size()
                f.write("Locations by district:\n")
                for (state, district), count in district_counts.items():
                    f.write(f"  {state} - {district}: {count} locations\n")
                f.write("\n")
            
            # Measurements summary
            f.write("MEASUREMENTS SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total measurements: {len(measurements_df)}\n")
            
            if not measurements_df.empty:
                f.write(f"Date range: {measurements_df['date'].min()} to {measurements_df['date'].max()}\n")
                f.write(f"Parameters monitored: {', '.join(measurements_df['parameter'].unique())}\n\n")
                
                param_counts = measurements_df['parameter'].value_counts()
                f.write("Measurements by parameter:\n")
                for param, count in param_counts.items():
                    f.write(f"  {param}: {count} measurements\n")
                f.write("\n")
            
            # District summary
            if not district_summary_df.empty:
                f.write("DISTRICT-WISE SUMMARY (TOP POLLUTANT LEVELS)\n")
                f.write("-" * 45 + "\n")
                
                for param in district_summary_df['parameter'].unique():
                    param_data = district_summary_df[district_summary_df['parameter'] == param]
                    f.write(f"\n{param.upper()} levels by district:\n")
                    param_data_sorted = param_data.sort_values('avg_value', ascending=False)
                    
                    for _, row in param_data_sorted.head(10).iterrows():
                        f.write(f"  {row['district']}: {row['avg_value']:.2f} (avg), "
                               f"{row['max_value']:.2f} (max), "
                               f"{row['measurement_count']} measurements\n")
        
        logger.info(f"Comprehensive report saved to: {report_file}")
    
    def run_analysis(self, days_back: int = 30, parameters: List[str] = None) -> bool:
        """
        Run the complete analysis pipeline
        
        Args:
            days_back: Number of days back to fetch data
            parameters: List of parameters to analyze
            
        Returns:
            bool: True if successful
        """
        logger.info("Starting Delhi NCR Air Quality Analysis")
        
        # Step 1: Load district boundaries
        if not self.load_district_boundaries():
            return False
        
        # Step 2: Get monitoring locations
        locations = self.get_monitoring_locations()
        if not locations:
            logger.error("No monitoring locations found")
            return False
        
        # Step 3: Assign districts to locations
        location_df = self.assign_districts_to_locations()
        if location_df.empty:
            logger.error("Failed to assign districts to locations")
            return False
        
        # Step 4: Get measurements
        logger.info(f"Fetching measurements for last {days_back} days...")
        measurements_df = self.get_measurements_for_locations(location_df, days_back, parameters)
        
        # Step 5: Generate district summary
        district_summary_df = self.generate_district_summary(measurements_df)
        
        # Step 6: Save results
        success = self.save_to_csv(location_df, measurements_df, district_summary_df)
        
        if success:
            logger.info("Analysis completed successfully!")
            logger.info(f"Results saved with timestamp: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        return success


def main():
    """
    Main function to run the analysis
    """
    # Initialize analyzer
    analyzer = DelhiNCRAirQualityAnalyzer()
    
    # Run analysis for last 30 days
    # You can modify parameters and days_back as needed
    parameters = ['pm25', 'pm10', 'no2', 'so2', 'o3', 'co']
    days_back = 30
    
    success = analyzer.run_analysis(days_back=days_back, parameters=parameters)
    
    if success:
        print("\n" + "="*60)
        print("Delhi NCR Air Quality Analysis Completed Successfully!")
        print("="*60)
        print(f"Check the generated CSV files and report in the current directory.")
        print(f"Analysis covered {days_back} days of data for {len(parameters)} parameters.")
    else:
        print("Analysis failed. Check the logs for details.")


if __name__ == "__main__":
    main()