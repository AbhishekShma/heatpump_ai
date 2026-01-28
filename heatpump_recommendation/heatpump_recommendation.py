import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict
from heatpump_recommendation_utils import row_to_dict

def heat_pump_recommendation(
    heat_load: float,
    db_url: str,
    recommendation_radius: float = 2,
    number_of_recommendations: int = 10
) -> List[Dict]:
    """
    Returns heat pump models whose heat_output_35_kw is within
    ±recommendation_radius kW of the given heat_load, sorted by cop_35 (descending).
    """ 

    lower_bound = heat_load - recommendation_radius

    # upper_bound = heat_load + recommendation_radius
    
    # Changed as per client's reqest for the upper bound to be equal to heat load
    upper_bound = heat_load


    sql = """
        SELECT
            id,
            manufacturer,
            model_type,
            heat_output_35_kw,
            cop_35,
            refrigerant,
            category
        FROM heat_pump_models
        WHERE heat_output_35_kw BETWEEN %s AND %s
        ORDER BY cop_35 DESC NULLS LAST
        LIMIT %s;
    """

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (lower_bound, upper_bound, number_of_recommendations))
            rows = cur.fetchall()

            result = []  # initialize list

            for row in rows:
                row_dict = row_to_dict(row)
                result.append(row_dict)

            # print(result)
            return result
    finally:
        conn.close()

