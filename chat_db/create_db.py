""" Create the database """
import sqlite3

con = sqlite3.connect("company_data.db")
cur = con.cursor()

cur.execute("CREATE TABLE clients(client_id, dni, phone, name, postal_code)")
cur.execute("""
    INSERT INTO clients VALUES
        ('8123912221', '88344024A', '693517860', 'Pedro Marquez', '28010'),
        ('3586293929', '92239284B', '691234567', 'Juan Sandoval', '06194'),
        ('4972639021', '02383983C', '689876543', 'Maria Lopez', '11051')
""")
con.commit()

cur.execute("CREATE TABLE client_features(client_id, phone_data_gb, wifi_speed, monthly_bill_euro)")
cur.execute("""
    INSERT INTO client_features VALUES
        ('8123912221', 50, 500, 69.9),
        ('3586293929', 10, 500, 59.9),
        ('4972639021', 25, 100, 39.9)
""")
con.commit()

cur.execute("CREATE TABLE client_puk_codes(client_id, puk_code)")
cur.execute("""
    INSERT INTO client_puk_codes VALUES
        ('8123912221', 34532457),
        ('3586293929', 78564335),
        ('4972639021', 63452725)
""")
con.commit()

cur.execute("CREATE TABLE current_incidents(postal_code, incident, reason, expected_time)")
cur.execute("""
    INSERT INTO current_incidents VALUES
        ('28010', true, 'network outage', '2 hours'),
        ('06194', true, 'equipment failure', '3 hours'),
        ('11051', false, NULL, NULL)
""")
con.commit()

cur.execute("CREATE TABLE available_phone_offers(phone_data_gb, monthly_bill_range, priority)")
cur.execute("""
    INSERT INTO available_phone_offers VALUES
        (10, '5-20', 'try to avoid'),
        (25, '15-30', 'medium'),
        (50, '25-40', 'high')
""")
con.commit()

cur.execute("CREATE TABLE available_wifi_offers(wifi_speed, monthly_bill_range, priority)")
cur.execute("""
    INSERT INTO available_wifi_offers VALUES
        (100, '10-25', 'medium'),
        (500, '25-40', 'high'),
        (1000, '50-80', 'low')
""")
con.commit()
