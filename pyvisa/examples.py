import pyvisa
import time
import csv
from datetime import datetime

def connect_dmm(resource_string):
    """Connect to DMM with proper configuration"""
    rm = pyvisa.ResourceManager()
    
    try:
        dmm = rm.open_resource(resource_string)
        dmm.timeout = 10000  # 10 second timeout
        dmm.write_termination = '\n'
        dmm.read_termination = '\n'
        
        # Identify the instrument
        idn = dmm.query("*IDN?")
        print(f"Connected to: {idn}")
        
        # Reset to known state
        dmm.write("*RST")
        dmm.write("*CLS")  # Clear error queue
        
        return dmm, rm
        
    except pyvisa.VisaIOError as e:
        print(f"Connection failed: {e}")
        rm.close()
        raise

# Example usage
dmm, rm = connect_dmm("GPIB0::20::INSTR")

def basic_measurements(dmm):
    """Perform all basic measurement types"""
    
    measurements = {}
    
    # DC Voltage (default range auto)
    dmm.write("CONF:VOLT:DC")
    time.sleep(0.1)
    dmm.write("READ?")
    measurements['dc_voltage'] = float(dmm.read())
    
    # AC Voltage
    dmm.write("CONF:VOLT:AC")
    time.sleep(0.1)
    dmm.write("READ?")
    measurements['ac_voltage'] = float(dmm.read())
    
    # DC Current (be careful with current measurements!)
    dmm.write("CONF:CURR:DC")
    time.sleep(0.1)
    dmm.write("READ?")
    measurements['dc_current'] = float(dmm.read())
    
    # Resistance (2-wire)
    dmm.write("CONF:RES")
    time.sleep(0.1)
    dmm.write("READ?")
    measurements['resistance'] = float(dmm.read())
    
    # 4-wire resistance (more accurate for low resistance)
    dmm.write("CONF:FRES")
    time.sleep(0.1)
    dmm.write("READ?")
    measurements['resistance_4wire'] = float(dmm.read())
    
    return measurements

# Example usage
results = basic_measurements(dmm)
for measurement, value in results.items():
    print(f"{measurement}: {value}")

class DMM_DataLogger:
    """Professional data logging class for DMM measurements"""
    
    def __init__(self, dmm, filename=None):
        self.dmm = dmm
        self.filename = filename or f"dmm_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.measurements = []
        
    def configure_measurement(self, measurement_type='VOLT:DC', range_val='AUTO', 
                            nplc=1, samples=1):
        """Configure measurement parameters"""
        
        # Set measurement function
        self.dmm.write(f"CONF:{measurement_type}")
        
        # Set range
        if range_val != 'AUTO':
            self.dmm.write(f"{measurement_type}:RANGE {range_val}")
        
        # Set integration time
        self.dmm.write(f"{measurement_type}:NPLC {nplc}")
        
        # Configure for multiple samples
        self.dmm.write(f"SAMP:COUN {samples}")
        
        print(f"Configured for {measurement_type}, Range: {range_val}, NPLC: {nplc}")
    
    def log_single_measurement(self):
        """Log a single measurement with timestamp"""
        
        timestamp = datetime.now()
        self.dmm.write("READ?")
        value = float(self.dmm.read())
        
        measurement = {
            'timestamp': timestamp,
            'value': value,
            'iso_time': timestamp.isoformat()
        }
        
        self.measurements.append(measurement)
        return measurement
    
    def continuous_logging(self, duration_minutes=10, interval_seconds=1):
        """Continuously log measurements for specified duration"""
        
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        measurement_count = 0
        
        print(f"Starting continuous logging for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early")
        
        try:
            while datetime.now().timestamp() < end_time:
                measurement = self.log_single_measurement()
                measurement_count += 1
                
                print(f"#{measurement_count}: {measurement['value']:.6f} at {measurement['timestamp'].strftime('%H:%M:%S')}")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\nLogging stopped by user after {measurement_count} measurements")
        
        self.save_to_csv()
        return self.measurements
    
    def save_to_csv(self):
        """Save measurements to CSV file"""
        
        if not self.measurements:
            print("No measurements to save")
            return
        
        with open(self.filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'iso_time', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for measurement in self.measurements:
                writer.writerow(measurement)
        
        print(f"Saved {len(self.measurements)} measurements to {self.filename}")
    
    def get_statistics(self):
        """Calculate statistics from logged data"""
        
        if not self.measurements:
            return None
        
        values = [m['value'] for m in self.measurements]
        
        import statistics
        stats = {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
        
        return stats

# Example usage
logger = DMM_DataLogger(dmm, "battery_monitoring.csv")
logger.configure_measurement('VOLT:DC', range_val=10, nplc=1)

# Log for 5 minutes, one measurement per second
measurements = logger.continuous_logging(duration_minutes=5, interval_seconds=1)

# Get statistics
stats = logger.get_statistics()
print(f"\nLogging Statistics:")
for key, value in stats.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.6f}")
    else:
        print(f"  {key}: {value}")

def battery_discharge_test(dmm, initial_voltage=12.0, cutoff_voltage=10.5):
    """Automated battery discharge test"""
    
    print("=== Battery Discharge Test ===")
    print(f"Monitoring voltage from {initial_voltage}V down to {cutoff_voltage}V")
    
    # Configure for battery voltage monitoring
    dmm.write("CONF:VOLT:DC")
    dmm.write("VOLT:DC:RANGE 100")  # Use 100V range for stability
    dmm.write("VOLT:DC:NPLC 1")    # 1 PLC for good balance of speed/accuracy
    
    start_time = datetime.now()
    measurements = []
    
    try:
        while True:
            # Take measurement
            dmm.write("READ?")
            voltage = float(dmm.read())
            current_time = datetime.now()
            elapsed_minutes = (current_time - start_time).total_seconds() / 60
            
            measurement = {
                'time_minutes': elapsed_minutes,
                'voltage': voltage,
                'timestamp': current_time
            }
            measurements.append(measurement)
            
            print(f"Time: {elapsed_minutes:6.1f} min, Voltage: {voltage:.3f} V")
            
            # Check cutoff condition
            if voltage <= cutoff_voltage:
                print(f"\nCutoff voltage {cutoff_voltage}V reached!")
                break
            
            # Check for unrealistic voltage (connection issues)
            if voltage < 0 or voltage > 50:
                print(f"Warning: Unusual voltage reading {voltage}V")
            
            time.sleep(60)  # Measure every minute
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    # Save results
    filename = f"battery_test_{start_time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['time_minutes', 'voltage', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(measurements)
    
    total_time = measurements[-1]['time_minutes'] if measurements else 0
    print(f"Test completed in {total_time:.1f} minutes")
    print(f"Results saved to {filename}")
    
    return measurements

# Example usage
battery_test_results = battery_discharge_test(dmm)

def resistor_tolerance_test(dmm, nominal_values, tolerance_percent=5):
    """Test multiple resistors for tolerance compliance"""
    
    print("=== Resistor Tolerance Test ===")
    
    # Configure for resistance measurement
    dmm.write("CONF:RES")
    dmm.write("RES:NPLC 10")  # High accuracy for component testing
    
    results = []
    
    for i, nominal in enumerate(nominal_values):
        input(f"\nConnect resistor #{i+1} (nominal {nominal} Ω) and press Enter...")
        
        # Take multiple measurements for accuracy
        measurements = []
        for j in range(5):
            dmm.write("READ?")
            value = float(dmm.read())
            measurements.append(value)
            time.sleep(0.2)
        
        # Calculate average
        avg_resistance = sum(measurements) / len(measurements)
        deviation_percent = ((avg_resistance - nominal) / nominal) * 100
        within_tolerance = abs(deviation_percent) <= tolerance_percent
        
        result = {
            'resistor_number': i + 1,
            'nominal_ohms': nominal,
            'measured_ohms': avg_resistance,
            'deviation_percent': deviation_percent,
            'within_tolerance': within_tolerance,
            'tolerance_limit': tolerance_percent
        }
        
        results.append(result)
        
        # Print result
        status = "PASS" if within_tolerance else "FAIL"
        print(f"Resistor #{i+1}: {avg_resistance:.2f} Ω ({deviation_percent:+.2f}%) - {status}")
    
    # Summary
    passed = sum(1 for r in results if r['within_tolerance'])
    print(f"\nTest Summary: {passed}/{len(results)} resistors passed tolerance test")
    
    return results

# Example usage
# Test 1kΩ, 10kΩ, 100kΩ resistors with 5% tolerance
#test_results = resistor_tolerance_test(dmm, [1000, 10000, 100000], tolerance_percent=5)