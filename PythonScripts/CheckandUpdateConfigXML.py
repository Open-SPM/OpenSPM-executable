from lxml import etree
from typing import List, Dict, Tuple, Optional


def find_case_insensitive(element: etree._Element, path: str, name: str) -> Optional[etree._Element]:
    elements = element.findall(path)
    return next((e for e in elements if e.find('Name').text.lower() == name.lower()), None)


def check_cluster(root: etree._Element, cluster_name: str, requirements: Dict[str, List[str]], find_func) -> List[str]:
    errors = []

    # Check for special cases - strings that are direct children of the root
    if cluster_name in ['FPGA', 'AFM system name', 'User name', 'XMLConfigVersion']:
        element = find_func(root, './/String', cluster_name)
        if element is None:
            errors.append(f"Missing {cluster_name} string")
        return errors

    cluster = find_func(root, './/Cluster', cluster_name)

    if cluster is None:
        return [f"Missing {cluster_name} cluster"]

    missing_clusters = [name for name in requirements.get('clusters', [])
                        if find_func(cluster, './/Cluster', name) is None]

    missing_dbls = [name for name in requirements.get('dbls', [])
                    if find_func(cluster, './/DBL', name) is None]

    if missing_clusters:
        errors.append(f"Missing clusters in {cluster_name}: {', '.join(missing_clusters)}")
    if missing_dbls:
        errors.append(f"Missing DBL elements in {cluster_name}: {', '.join(missing_dbls)}")

    return errors


def create_derate_cluster() -> etree._Element:
    """Create a new Derate cluster with default values."""
    derate = etree.Element("Cluster")
    name = etree.SubElement(derate, "Name")
    name.text = "Derate"
    num_elts = etree.SubElement(derate, "NumElts")
    num_elts.text = "3"

    # Add Derate X
    dbl_x = etree.SubElement(derate, "DBL")
    name_x = etree.SubElement(dbl_x, "Name")
    name_x.text = "Derate X"
    val_x = etree.SubElement(dbl_x, "Val")
    val_x.text = "0.00000000000000"

    # Add Derate Y
    dbl_y = etree.SubElement(derate, "DBL")
    name_y = etree.SubElement(dbl_y, "Name")
    name_y.text = "Derate Y"
    val_y = etree.SubElement(dbl_y, "Val")
    val_y.text = "0.00000000000000"

    # Add Derate Z
    dbl_z = etree.SubElement(derate, "DBL")
    name_z = etree.SubElement(dbl_z, "Name")
    name_z.text = "Derate Z"
    val_z = etree.SubElement(dbl_z, "Val")
    val_z.text = "0.00000000000000"

    return derate


def create_offset_sens_cluster() -> etree._Element:
    """Create a new Offset Sens cluster with temporary values that will be updated."""
    offset_sens = etree.Element("Cluster")
    name = etree.SubElement(offset_sens, "Name")
    name.text = "Offset Sens"
    num_elts = etree.SubElement(offset_sens, "NumElts")
    num_elts.text = "3"

    # Add Offset Sens X
    dbl_x = etree.SubElement(offset_sens, "DBL")
    name_x = etree.SubElement(dbl_x, "Name")
    name_x.text = "Offset Sens X"
    val_x = etree.SubElement(dbl_x, "Val")
    val_x.text = "0.00000000000000"  # Initial value, will be replaced

    # Add Offset Sens Y
    dbl_y = etree.SubElement(offset_sens, "DBL")
    name_y = etree.SubElement(dbl_y, "Name")
    name_y.text = "Offset Sens Y"
    val_y = etree.SubElement(dbl_y, "Val")
    val_y.text = "0.00000000000000"  # Initial value, will be replaced

    # Add Offset Sens Z
    dbl_z = etree.SubElement(offset_sens, "DBL")
    name_z = etree.SubElement(dbl_z, "Name")
    name_z.text = "Offset Sens Z"
    val_z = etree.SubElement(dbl_z, "Val")
    val_z.text = "0.00000000000000"  # Initial value, will be replaced

    return offset_sens


def create_calib_vol_element() -> etree._Element:
    """Create a new Calib Vol DBL element with default value."""
    dbl = etree.Element("DBL")
    name = etree.SubElement(dbl, "Name")
    name.text = "Calib Vol"
    val = etree.SubElement(dbl, "Val")
    val.text = "450.00000000000000"
    return dbl


def create_shear_factor_element() -> etree._Element:
    """Create a new Shear Factor DBL element with default value of 1."""
    dbl = etree.Element("DBL")
    name = etree.SubElement(dbl, "Name")
    name.text = "Shear Factor"
    val = etree.SubElement(dbl, "Val")
    val.text = "1.00000000000000"
    return dbl


def calculate_sensitivity_values(root: etree._Element) -> None:
    """
    Calculate Sensitivity and Offset Sensitivity values when missing elements are added.
    Only called when all 4 elements (Derate, Offset Sens, Calib Vol, and Shear Factor) were missing.

    Args:
        root: XML root element
    """
    try:
        # Find Calibration Parameters cluster
        calib_params = find_case_insensitive(root, './/Cluster', 'Calibration Parameters')
        if calib_params is None:
            print("No Calibration Parameters found")
            return

        # Get Range cluster
        range_cluster = find_case_insensitive(calib_params, './/Cluster', 'Range')
        if range_cluster is None:
            print("No Range cluster found")
            return

        # Default calibration voltage is 450
        calib_vol = 450.0

        # Get Range values
        range_x_element = find_case_insensitive(range_cluster, './/DBL', 'Range X')
        range_y_element = find_case_insensitive(range_cluster, './/DBL', 'Range Y')
        range_z_element = find_case_insensitive(range_cluster, './/DBL', 'Range Z')

        if range_x_element is None or range_y_element is None or range_z_element is None:
            print("Missing Range X, Y, or Z elements")
            return

        range_x = float(range_x_element.find('Val').text) if range_x_element.find('Val') is not None else 0
        range_y = float(range_y_element.find('Val').text) if range_y_element.find('Val') is not None else 0
        range_z = float(range_z_element.find('Val').text) if range_z_element.find('Val') is not None else 0

        # Calculate sensitivity values
        sens_x_value = range_x / calib_vol
        sens_y_value = range_y / calib_vol
        sens_z_value = range_z / calib_vol

        print(f"Calculated sensitivity values: X={sens_x_value:.16E}, Y={sens_y_value:.16E}, Z={sens_z_value:.16E}")

        # Update Sensitivity values
        sensitivity_cluster = find_case_insensitive(calib_params, './/Cluster', 'Sensitivity')
        if sensitivity_cluster is not None:
            sens_x_element = find_case_insensitive(sensitivity_cluster, './/DBL', 'Sens X')
            sens_y_element = find_case_insensitive(sensitivity_cluster, './/DBL', 'Sens Y')
            sens_z_element = find_case_insensitive(sensitivity_cluster, './/DBL', 'Sens Z')

            if sens_x_element is not None and sens_x_element.find('Val') is not None:
                sens_x_element.find('Val').text = f"{sens_x_value:.16E}"

            if sens_y_element is not None and sens_y_element.find('Val') is not None:
                sens_y_element.find('Val').text = f"{sens_y_value:.16E}"

            if sens_z_element is not None and sens_z_element.find('Val') is not None:
                sens_z_element.find('Val').text = f"{sens_z_value:.16E}"
        else:
            print("No Sensitivity cluster found")

        # Find the Offset Sens cluster that was JUST added
        offset_sens_cluster = find_case_insensitive(calib_params, './/Cluster', 'Offset Sens')
        if offset_sens_cluster is None:
            print("No Offset Sens cluster found")
            return

        # Get the Offset Sens elements
        offset_sens_x_element = find_case_insensitive(offset_sens_cluster, './/DBL', 'Offset Sens X')
        offset_sens_y_element = find_case_insensitive(offset_sens_cluster, './/DBL', 'Offset Sens Y')
        offset_sens_z_element = find_case_insensitive(offset_sens_cluster, './/DBL', 'Offset Sens Z')

        # Check if we found all elements
        if offset_sens_x_element is None or offset_sens_y_element is None or offset_sens_z_element is None:
            print("Missing Offset Sens X, Y, or Z elements")
            return

        # Get the Val elements
        offset_sens_x_val = offset_sens_x_element.find('Val')
        offset_sens_y_val = offset_sens_y_element.find('Val')
        offset_sens_z_val = offset_sens_z_element.find('Val')

        # Check if we found all Val elements
        if offset_sens_x_val is None or offset_sens_y_val is None or offset_sens_z_val is None:
            print("Missing Offset Sens X, Y, or Z Val elements")
            return

        # Update the values
        offset_sens_x_val.text = f"{sens_x_value:.16E}"
        offset_sens_y_val.text = f"{sens_y_value:.16E}"
        offset_sens_z_val.text = f"{sens_z_value:.16E}"

        print(
            f"Updated Offset Sens values: X={offset_sens_x_val.text}, Y={offset_sens_y_val.text}, Z={offset_sens_z_val.text}")

    except Exception as e:
        print(f"Error calculating sensitivity values: {str(e)}")


def check_structure(xml_input: str) -> Tuple[bool, str, str]:
    """
    Checks if the XML structure meets the required format.

    Args:
        xml_input: XML string to check

    Returns:
        Tuple containing:
        - Boolean indicating if the XML is valid
        - Error message or success message
        - The original XML string (unchanged)
    """
    required_structure = {
        'Piezo': {
            'clusters': ['Calibration Parameters']
        },
        'Calibration Parameters': {
            'clusters': ['Sensitivity', 'Range', 'HV gain', 'Derate', 'Offset Sens'],
            'dbls': ['Calib Vol', 'Shear Factor']
        },
        'Cantilever': {
            'clusters': []
        },
        'FPGA': {
            'clusters': []
        },
        'AFM system name': {
            'clusters': []
        },
        'User name': {
            'clusters': []
        },
        'XMLConfigVersion': {
            'clusters': []
        }
    }
    try:
        root = etree.fromstring(xml_input)

        if find_case_insensitive(root, '.', 'InfoConfigIn') is None:
            return False, "Missing InfoConfigIn cluster", xml_input

        all_errors = []
        for cluster_name, requirements in required_structure.items():
            errors = check_cluster(root, cluster_name, requirements, find_case_insensitive)
            all_errors.extend(errors)

        return (len(all_errors) == 0, "; ".join(all_errors) if all_errors else "Valid structure", xml_input)

    except etree.XMLSyntaxError as e:
        return False, f"Invalid XML syntax: {str(e)}", xml_input
    except Exception as e:
        return False, f"Error: {str(e)}", xml_input


def fix_missing_elements(xml_input: str) -> Tuple[bool, str, Optional[str]]:
    """
    Checks XML structure and fixes missing elements:
    1. Adds XMLConfigVersion string if missing
    2. Adds Derate, Offset Sens, Calib Vol, and Shear Factor if all are missing
    Also calculates Sensitivity and Offset Sensitivity values based on Range divided by 450
    (default calibration voltage).

    Args:
        xml_input: XML string to check and fix

    Returns:
        Tuple containing:
        - Boolean indicating if the XML is valid (after fixing)
        - Error message or success message
        - Modified XML string if fixed, None otherwise
    """
    try:
        root = etree.fromstring(xml_input)
        changes_made = False
        messages = []

        # Check if XMLConfigVersion element exists and add if missing
        xml_config_version = find_case_insensitive(root, './/String', 'XMLConfigVersion')
        if xml_config_version is None:
            print("XMLConfigVersion missing, adding it now...")

            # Add XMLConfigVersion element
            root.append(create_xml_config_version_element())

            # Update NumElts for InfoConfigIn cluster if found
            if root.tag == "Cluster" and root.find('Name') is not None and root.find('Name').text == "InfoConfigIn":
                num_elts = root.find('NumElts')
                if num_elts is not None:
                    current_elts = int(num_elts.text)
                    num_elts.text = str(current_elts + 1)
                    print(f"Updated InfoConfigIn NumElts to {num_elts.text}")

            changes_made = True
            messages.append("Added XMLConfigVersion element")

        # Find Calibration Parameters cluster
        calib_params = find_case_insensitive(root, './/Cluster', 'Calibration Parameters')
        if calib_params is None:
            return False, "Missing Calibration Parameters cluster", None

        # Check if all specified elements are missing
        derate_missing = find_case_insensitive(calib_params, './/Cluster', 'Derate') is None
        offset_sens_missing = find_case_insensitive(calib_params, './/Cluster', 'Offset Sens') is None
        calib_vol_missing = find_case_insensitive(calib_params, './/DBL', 'Calib Vol') is None
        shear_factor_missing = find_case_insensitive(calib_params, './/DBL', 'Shear Factor') is None

        # If all are missing, add them
        if derate_missing and offset_sens_missing and calib_vol_missing and shear_factor_missing:
            print("All four elements missing, adding them now...")

            # Create and add missing elements
            calib_params.append(create_derate_cluster())  # All zeros
            calib_params.append(create_offset_sens_cluster())  # Will be calculated
            calib_params.append(create_calib_vol_element())  # Default 450
            calib_params.append(create_shear_factor_element())  # Value of 1

            # Update NumElts
            num_elts = calib_params.find('NumElts')
            if num_elts is not None:
                current_elts = int(num_elts.text)
                # Adding 4 new elements (2 clusters and 2 DBLs)
                num_elts.text = str(current_elts + 4)
                print(f"Updated NumElts to {num_elts.text}")

            # Calculate sensitivity values based on Range/450
            print("Calculating sensitivity values...")
            calculate_sensitivity_values(root)

            # Make a debugging copy of the XML to check values
            debug_xml = etree.tostring(root, encoding='unicode')
            print("\nDebug XML after fixing and calculating sensitivity values:")

            # Check the Offset Sens values in the XML
            offset_sens_cluster = find_case_insensitive(root, './/Cluster', 'Offset Sens')
            if offset_sens_cluster is not None:
                print("\nOffset Sens cluster found in final XML:")
                for child in offset_sens_cluster:
                    if child.tag == "DBL":
                        name_elem = child.find('Name')
                        val_elem = child.find('Val')
                        if name_elem is not None and val_elem is not None:
                            print(f"{name_elem.text}: {val_elem.text}")

            changes_made = True
            messages.append("Fixed missing elements and calculated sensitivity values")

        # If any changes were made, return the modified XML
        if changes_made:
            final_xml = etree.tostring(root, encoding='unicode')
            return True, "; ".join(messages), final_xml

        # If no changes were needed, perform normal check
        valid, message, original_xml = check_structure(xml_input)
        return valid, message, xml_input

    except etree.XMLSyntaxError as e:
        return False, f"Invalid XML syntax: {str(e)}", xml_input
    except Exception as e:
        print(f"Exception in fix_missing_elements: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}", xml_input


def create_xml_config_version_element() -> etree._Element:
    """Create a new XMLConfigVersion String element with default value."""
    string = etree.Element("String")
    name = etree.SubElement(string, "Name")
    name.text = "XMLConfigVersion"
    val = etree.SubElement(string, "Val")
    val.text = "1.0"
    return string


if __name__ == "__main__":
    # Test with modified XML missing the elements we want to fix
    xml_string = '''<Cluster>
<Name>InfoConfigIn</Name>
<NumElts>5</NumElts>
<Cluster>
<Name>Piezo</Name>
<NumElts>2</NumElts>
<String>
<Name>Calibration name</Name>
<Val>Calibration File</Val>
</String>
<Cluster>
<Name>Calibration Parameters</Name>
<NumElts>3</NumElts>
<Cluster>
<Name>Sensitivity</Name>
<NumElts>3</NumElts>
<DBL>
<Name>Sens X</Name>
<Val>1.00000000000000E-6</Val>
</DBL>
<DBL>
<Name>Sens Y</Name>
<Val>1.00000000000000E-6</Val>
</DBL>
<DBL>
<Name>Sens Z</Name>
<Val>0.00000000000000</Val>
</DBL>
</Cluster>
<Cluster>
<Name>Range</Name>
<NumElts>3</NumElts>
<DBL>
<Name>Range X</Name>
<Val>4.50000000000000E-4</Val>
</DBL>
<DBL>
<Name>Range Y</Name>
<Val>4.50000000000000E-4</Val>
</DBL>
<DBL>
<Name>Range Z</Name>
<Val>3.50000000000000E-6</Val>
</DBL>
</Cluster>
<Cluster>
<Name>HV gain</Name>
<NumElts>3</NumElts>
<I32>
<Name>HV gain X</Name>
<Val>0</Val>
</I32>
<I32>
<Name>HV gain Y</Name>
<Val>0</Val>
</I32>
<I32>
<Name>HV gain Z</Name>
<Val>0</Val>
</I32>
</Cluster>
</Cluster>
</Cluster>
<Cluster>
<Name>Cantilever</Name>
<NumElts>18</NumElts>
<String>
<Name>Model</Name>
<Val>Trilayer</Val>
</String>
<String>
<Name>Info</Name>
<Val></Val>
</String>
<DBL>
<Name>Length [m]</Name>
<Val>1.50000000000000E-4</Val>
</DBL>
<DBL>
<Name>Width [m]</Name>
<Val>3.00000000000000E-5</Val>
</DBL>
<DBL>
<Name>Thickness [m]</Name>
<Val>1.00000000000000E-6</Val>
</DBL>
<DBL>
<Name>Young's modulus [Pa]</Name>
<Val>170000000000.00000000000000</Val>
</DBL>
<DBL>
<Name>Poisson's ratio</Name>
<Val>0.27000000000000</Val>
</DBL>
<DBL>
<Name>Density [kg/m3]</Name>
<Val>2329.00000000000000</Val>
</DBL>
<DBL>
<Name>Nominal resonance frequency [Hz]</Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Nominal spring constant [N/m]</Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Coating thickness [m]</Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Coating Young's modulus [Pa] </Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Coating Poisson's ratio</Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Coating density [kg/m3]</Name>
<Val>-1.00000000000000</Val>
</DBL>
<DBL>
<Name>Reserved 1</Name>
<Val>0.00000000000000</Val>
</DBL>
<DBL>
<Name>Reserved 2</Name>
<Val>-1.00000000000000</Val>
</DBL>
<EW>
<Name></Name>
<Choice>Rectangular</Choice>
<Choice>Triangular</Choice>
<Val>0</Val>
</EW>
<EW>
<Name></Name>
<Choice>Uncoated</Choice>
<Choice>Coated</Choice>
<Val>0</Val>
</EW>
</Cluster>
<String>
<Name>FPGA</Name>
<Val>USB7856R</Val>
</String>
<String>
<Name>AFM system name</Name>
<Val>AFM</Val>
</String>
<String>
<Name>User name</Name>
<Val>UserName</Val>
</String>
</Cluster>'''

    # First, check the structure without fixing
    success, error_message, original_xml = check_structure(xml_string)
    print(f"Before fixing - Valid: {success}, Message: {error_message}")

    # Fix missing elements including XMLConfigVersion
    success, error_message, fixed_xml = fix_missing_elements(xml_string)
    print(f"After fixing elements - Valid: {success}, Message: {error_message}")

    if fixed_xml:
        # Verify the fixed XML
        verify_success, verify_message, _ = check_structure(fixed_xml)
        print(f"Verification of fixed XML - Valid: {verify_success}, Message: {verify_message}")