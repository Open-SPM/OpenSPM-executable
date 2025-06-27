from lxml import etree
from typing import List, Dict, Tuple, Optional


def text_matches(elem, text_to_match):
    """Case-insensitive text matching for XML elements."""
    if elem is None or elem.text is None:
        return False
    return elem.text.lower() == text_to_match.lower()


def find_element_by_name(parent, element_type, name_to_find):
    """
    Find an element of a specific type with a specific name, case-insensitive.

    Args:
        parent: Parent element to search in
        element_type: Tag name to search for (String, Cluster, DBL, etc.)
        name_to_find: Name to match

    Returns:
        Matching element or None if not found
    """
    # Find all elements of the specified type
    elements = parent.xpath(f".//*[local-name()='{element_type}']")

    # Look for one with a Name child that matches
    for elem in elements:
        for child in elem:
            if child.tag.endswith('Name') and text_matches(child, name_to_find):
                return elem

    return None


def create_derate_cluster() -> etree._Element:
    """Create a new Derate cluster with default values (all zeros)."""
    derate = etree.Element("Cluster")

    name = etree.SubElement(derate, "Name")
    name.text = "Derate"
    name.tail = "\n"

    num_elts = etree.SubElement(derate, "NumElts")
    num_elts.text = "3"
    num_elts.tail = "\n"

    # Add Derate X
    dbl_x = etree.SubElement(derate, "DBL")
    dbl_x.tail = "\n"

    name_x = etree.SubElement(dbl_x, "Name")
    name_x.text = "Derate X"
    name_x.tail = "\n"

    val_x = etree.SubElement(dbl_x, "Val")
    val_x.text = "0.00000000000000"
    val_x.tail = "\n"

    # Add Derate Y
    dbl_y = etree.SubElement(derate, "DBL")
    dbl_y.tail = "\n"

    name_y = etree.SubElement(dbl_y, "Name")
    name_y.text = "Derate Y"
    name_y.tail = "\n"

    val_y = etree.SubElement(dbl_y, "Val")
    val_y.text = "0.00000000000000"
    val_y.tail = "\n"

    # Add Derate Z
    dbl_z = etree.SubElement(derate, "DBL")
    dbl_z.tail = "\n"

    name_z = etree.SubElement(dbl_z, "Name")
    name_z.text = "Derate Z"
    name_z.tail = "\n"

    val_z = etree.SubElement(dbl_z, "Val")
    val_z.text = "0.00000000000000"
    val_z.tail = "\n"

    return derate


def create_offset_sens_cluster() -> etree._Element:
    """Create a new Offset Sens cluster with initial values that will be updated."""
    offset_sens = etree.Element("Cluster")

    name = etree.SubElement(offset_sens, "Name")
    name.text = "Offset Sens"
    name.tail = "\n"

    num_elts = etree.SubElement(offset_sens, "NumElts")
    num_elts.text = "3"
    num_elts.tail = "\n"

    # Add Offset Sens X
    dbl_x = etree.SubElement(offset_sens, "DBL")
    dbl_x.tail = "\n"

    name_x = etree.SubElement(dbl_x, "Name")
    name_x.text = "Offset Sens X"
    name_x.tail = "\n"

    val_x = etree.SubElement(dbl_x, "Val")
    val_x.text = "0.00000000000000"  # Initial value, will be replaced
    val_x.tail = "\n"

    # Add Offset Sens Y
    dbl_y = etree.SubElement(offset_sens, "DBL")
    dbl_y.tail = "\n"

    name_y = etree.SubElement(dbl_y, "Name")
    name_y.text = "Offset Sens Y"
    name_y.tail = "\n"

    val_y = etree.SubElement(dbl_y, "Val")
    val_y.text = "0.00000000000000"  # Initial value, will be replaced
    val_y.tail = "\n"

    # Add Offset Sens Z
    dbl_z = etree.SubElement(offset_sens, "DBL")
    dbl_z.tail = "\n"

    name_z = etree.SubElement(dbl_z, "Name")
    name_z.text = "Offset Sens Z"
    name_z.tail = "\n"

    val_z = etree.SubElement(dbl_z, "Val")
    val_z.text = "0.00000000000000"  # Initial value, will be replaced
    val_z.tail = "\n"

    return offset_sens


def create_calib_vol_element() -> etree._Element:
    """Create a new Calib Vol DBL element with default value (450)."""
    dbl = etree.Element("DBL")
    dbl.tail = "\n"

    name = etree.SubElement(dbl, "Name")
    name.text = "Calib Vol"
    name.tail = "\n"

    val = etree.SubElement(dbl, "Val")
    val.text = "450.00000000000000"
    val.tail = "\n"

    return dbl


def create_shear_factor_element() -> etree._Element:
    """Create a new Shear Factor DBL element with default value (1)."""
    dbl = etree.Element("DBL")
    dbl.tail = "\n"

    name = etree.SubElement(dbl, "Name")
    name.text = "Shear Factor"
    name.tail = "\n"

    val = etree.SubElement(dbl, "Val")
    val.text = "1.00000000000000"
    val.tail = "\n"

    return dbl


def calculate_sensitivity_values(cal_params):
    """
    Calculate and update sensitivity values based on Range/450.

    Args:
        cal_params: Calibration Parameters cluster element
    """
    try:
        # Default calibration voltage is 450
        calib_vol = 450.0

        # Get Range cluster
        range_cluster = find_element_by_name(cal_params, 'Cluster', 'Range')
        if range_cluster is None:
            print("No Range cluster found")
            return

        # Get Range values
        range_x_elem = find_element_by_name(range_cluster, 'DBL', 'Range X')
        range_y_elem = find_element_by_name(range_cluster, 'DBL', 'Range Y')
        range_z_elem = find_element_by_name(range_cluster, 'DBL', 'Range Z')

        if range_x_elem is None or range_y_elem is None or range_z_elem is None:
            print("Missing Range X, Y, or Z elements")
            return

        # Find Val elements - using XPath to find all Val elements inside each DBL
        range_x_val = range_x_elem.xpath('.//Val')[0] if range_x_elem.xpath('.//Val') else None
        range_y_val = range_y_elem.xpath('.//Val')[0] if range_y_elem.xpath('.//Val') else None
        range_z_val = range_z_elem.xpath('.//Val')[0] if range_z_elem.xpath('.//Val') else None

        # Fallback option - iterate through children if XPath doesn't work
        if range_x_val is None:
            for child in range_x_elem:
                if child.tag.endswith('Val'):
                    range_x_val = child
                    break

        if range_y_val is None:
            for child in range_y_elem:
                if child.tag.endswith('Val'):
                    range_y_val = child
                    break

        if range_z_val is None:
            for child in range_z_elem:
                if child.tag.endswith('Val'):
                    range_z_val = child
                    break

        # Print range values for debugging
        if range_x_val is not None and range_y_val is not None and range_z_val is not None:
            print(f"Range values: X={range_x_val.text}, Y={range_y_val.text}, Z={range_z_val.text}")
        else:
            print("Could not find all Val elements for ranges")
            print(f"Range X Val found: {range_x_val is not None}")
            print(f"Range Y Val found: {range_y_val is not None}")
            print(f"Range Z Val found: {range_z_val is not None}")
            return

        # Calculate sensitivity values
        range_x = float(range_x_val.text) if range_x_val is not None else 0
        range_y = float(range_y_val.text) if range_y_val is not None else 0
        range_z = float(range_z_val.text) if range_z_val is not None else 0

        # Calculate sensitivity values
        sens_x_value = range_x / calib_vol
        sens_y_value = range_y / calib_vol
        sens_z_value = range_z / calib_vol

        print(f"Calculated sensitivity values: X={sens_x_value:.16E}, Y={sens_y_value:.16E}, Z={sens_z_value:.16E}")

        # Update Sensitivity values
        sens_cluster = find_element_by_name(cal_params, 'Cluster', 'Sensitivity')
        if sens_cluster is not None:
            sens_x_elem = find_element_by_name(sens_cluster, 'DBL', 'Sens X')
            sens_y_elem = find_element_by_name(sens_cluster, 'DBL', 'Sens Y')
            sens_z_elem = find_element_by_name(sens_cluster, 'DBL', 'Sens Z')

            if sens_x_elem is not None:
                # Find Val element using the same approach as above
                sens_x_val = sens_x_elem.xpath('.//Val')[0] if sens_x_elem.xpath('.//Val') else None
                if sens_x_val is None:
                    for child in sens_x_elem:
                        if child.tag.endswith('Val'):
                            sens_x_val = child
                            break

                if sens_x_val is not None:
                    sens_x_val.text = f"{sens_x_value:.16E}"
                    print(f"Updated Sens X to {sens_x_val.text}")
                else:
                    print("Could not find Val element for Sens X")

            if sens_y_elem is not None:
                # Find Val element using the same approach as above
                sens_y_val = sens_y_elem.xpath('.//Val')[0] if sens_y_elem.xpath('.//Val') else None
                if sens_y_val is None:
                    for child in sens_y_elem:
                        if child.tag.endswith('Val'):
                            sens_y_val = child
                            break

                if sens_y_val is not None:
                    sens_y_val.text = f"{sens_y_value:.16E}"
                    print(f"Updated Sens Y to {sens_y_val.text}")
                else:
                    print("Could not find Val element for Sens Y")

            if sens_z_elem is not None:
                # Find Val element using the same approach as above
                sens_z_val = sens_z_elem.xpath('.//Val')[0] if sens_z_elem.xpath('.//Val') else None
                if sens_z_val is None:
                    for child in sens_z_elem:
                        if child.tag.endswith('Val'):
                            sens_z_val = child
                            break

                if sens_z_val is not None:
                    sens_z_val.text = f"{sens_z_value:.16E}"
                    print(f"Updated Sens Z to {sens_z_val.text}")
                else:
                    print("Could not find Val element for Sens Z")

        # Update Offset Sens values - must be a newly added cluster
        offset_sens = find_element_by_name(cal_params, 'Cluster', 'Offset Sens')
        if offset_sens is not None:
            offset_x_elem = find_element_by_name(offset_sens, 'DBL', 'Offset Sens X')
            offset_y_elem = find_element_by_name(offset_sens, 'DBL', 'Offset Sens Y')
            offset_z_elem = find_element_by_name(offset_sens, 'DBL', 'Offset Sens Z')

            if offset_x_elem is not None:
                # Find Val element using the same approach as above
                offset_x_val = offset_x_elem.xpath('.//Val')[0] if offset_x_elem.xpath('.//Val') else None
                if offset_x_val is None:
                    for child in offset_x_elem:
                        if child.tag.endswith('Val'):
                            offset_x_val = child
                            break

                if offset_x_val is not None:
                    offset_x_val.text = f"{sens_x_value:.16E}"
                    print(f"Updated Offset Sens X to {offset_x_val.text}")
                else:
                    print("Could not find Val element for Offset Sens X")

            if offset_y_elem is not None:
                # Find Val element using the same approach as above
                offset_y_val = offset_y_elem.xpath('.//Val')[0] if offset_y_elem.xpath('.//Val') else None
                if offset_y_val is None:
                    for child in offset_y_elem:
                        if child.tag.endswith('Val'):
                            offset_y_val = child
                            break

                if offset_y_val is not None:
                    offset_y_val.text = f"{sens_y_value:.16E}"
                    print(f"Updated Offset Sens Y to {offset_y_val.text}")
                else:
                    print("Could not find Val element for Offset Sens Y")

            if offset_z_elem is not None:
                # Find Val element using the same approach as above
                offset_z_val = offset_z_elem.xpath('.//Val')[0] if offset_z_elem.xpath('.//Val') else None
                if offset_z_val is None:
                    for child in offset_z_elem:
                        if child.tag.endswith('Val'):
                            offset_z_val = child
                            break

                if offset_z_val is not None:
                    offset_z_val.text = f"{sens_z_value:.16E}"
                    print(f"Updated Offset Sens Z to {offset_z_val.text}")
                else:
                    print("Could not find Val element for Offset Sens Z")

    except Exception as e:
        print(f"Error calculating sensitivity values: {str(e)}")
        import traceback
        traceback.print_exc()


def check_structure(xml_input: str) -> Tuple[bool, str, str]:
    """
    Check if the XML contains a valid list of calibration parameters.

    Args:
        xml_input: XML string to check

    Returns:
        Tuple containing:
        - Boolean indicating if the XML is valid
        - Error message or success message
        - The original XML string (unchanged)
    """
    # Define the required structure for calibrations
    required_structure = {
        'clusters': ['Sensitivity', 'Range', 'HV gain', 'Derate', 'Offset Sens'],
        'dbls': ['Calib Vol', 'Shear Factor']
    }

    try:
        root = etree.fromstring(xml_input)

        # Find all clusters that might be calibration entries
        all_clusters = root.xpath(".//*[local-name()='Cluster']")
        calibration_entries = []

        # Find those that have a String child with Name="Calibration name"
        for cluster in all_clusters:
            # Use our custom finder for case-insensitive matching
            if find_element_by_name(cluster, 'String', 'Calibration name') is not None:
                calibration_entries.append(cluster)

        if not calibration_entries:
            return False, "No calibration entries found", xml_input

        all_errors = []

        # Check each calibration entry
        for i, cal_entry in enumerate(calibration_entries):
            # Get the calibration name for better error messages
            cal_name_elem = find_element_by_name(cal_entry, 'String', 'Calibration name')
            cal_name = cal_name_elem.find('Val').text if cal_name_elem is not None and cal_name_elem.find(
                'Val') is not None else f"Entry #{i}"

            # Find the Calibration Parameters cluster using case-insensitive matching
            cal_params = find_element_by_name(cal_entry, 'Cluster', 'Calibration Parameters')

            if cal_params is None:
                all_errors.append(f"{cal_name}: Missing Calibration Parameters cluster")
                continue

            # Check for required clusters
            for cluster_name in required_structure['clusters']:
                if find_element_by_name(cal_params, 'Cluster', cluster_name) is None:
                    all_errors.append(f"{cal_name}: Missing {cluster_name} cluster")

            # Check for required DBL elements
            for dbl_name in required_structure['dbls']:
                if find_element_by_name(cal_params, 'DBL', dbl_name) is None:
                    all_errors.append(f"{cal_name}: Missing {dbl_name} DBL element")

        return (len(all_errors) == 0,
                "; ".join(all_errors) if all_errors else "Valid structure",
                xml_input)

    except etree.XMLSyntaxError as e:
        return False, f"Invalid XML syntax: {str(e)}", xml_input
    except Exception as e:
        print(f"Error checking structure: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}", xml_input


def fix_missing_elements(xml_input: str) -> Tuple[bool, str, Optional[str]]:
    """
    Fix calibration elements that are missing all four required elements.

    Args:
        xml_input: XML string to check and fix

    Returns:
        Tuple containing:
        - Boolean indicating if the fix was successful
        - Message about the fix
        - Fixed XML string or None if no fixes were needed
    """
    # Define the elements we want to check for
    target_elements = {
        'clusters': ['Derate', 'Offset Sens'],
        'dbls': ['Calib Vol', 'Shear Factor']
    }

    try:
        root = etree.fromstring(xml_input)

        # Find all clusters that might be calibration entries
        all_clusters = root.xpath(".//*[local-name()='Cluster']")
        calibration_entries = []

        # Find those that have a String child with Name="Calibration name"
        for cluster in all_clusters:
            # Use our custom finder for case-insensitive matching
            if find_element_by_name(cluster, 'String', 'Calibration name') is not None:
                calibration_entries.append(cluster)

        if not calibration_entries:
            return False, "No calibration entries found", None

        fixed_any = False
        fixed_count = 0

        # Process each calibration entry
        for cal_entry in calibration_entries:
            # Get the calibration name for better messages
            cal_name_elem = find_element_by_name(cal_entry, 'String', 'Calibration name')
            cal_name = cal_name_elem.find('Val').text if cal_name_elem is not None and cal_name_elem.find(
                'Val') is not None else f"Entry #{fixed_count}"

            # Find the Calibration Parameters cluster
            cal_params = find_element_by_name(cal_entry, 'Cluster', 'Calibration Parameters')

            if cal_params is None:
                continue

            # Check if all four target elements are missing
            missing_clusters = []
            for cluster_name in target_elements['clusters']:
                if find_element_by_name(cal_params, 'Cluster', cluster_name) is None:
                    missing_clusters.append(cluster_name)

            missing_dbls = []
            for dbl_name in target_elements['dbls']:
                if find_element_by_name(cal_params, 'DBL', dbl_name) is None:
                    missing_dbls.append(dbl_name)

            # Only fix if all four elements are missing
            if len(missing_clusters) == len(target_elements['clusters']) and \
                    len(missing_dbls) == len(target_elements['dbls']):
                print(f"Fixing calibration '{cal_name}'")

                # Create new elements with proper formatting
                # Add the missing elements with line breaks
                derate = create_derate_cluster()
                derate.tail = "\n"
                cal_params.append(derate)

                offset_sens = create_offset_sens_cluster()
                offset_sens.tail = "\n"
                cal_params.append(offset_sens)

                calib_vol = create_calib_vol_element()
                calib_vol.tail = "\n"
                cal_params.append(calib_vol)

                shear_factor = create_shear_factor_element()
                shear_factor.tail = "\n"
                cal_params.append(shear_factor)

                # Update NumElts
                num_elts = cal_params.find('NumElts')
                if num_elts is not None:
                    current_elts = int(num_elts.text)
                    # Adding 4 new elements (2 clusters and 2 DBLs)
                    num_elts.text = str(current_elts + 4)
                    print(f"Updated NumElts to {num_elts.text}")

                # Calculate sensitivity values
                calculate_sensitivity_values(cal_params)

                fixed_any = True
                fixed_count += 1

        if fixed_any:
            # Convert the XML tree back to a string with proper indentation
            fixed_xml = etree.tostring(root, encoding='unicode', pretty_print=True)
            if not fixed_xml or "pretty_print" not in str(etree.tostring.__code__):
                # If pretty_print is not available, use a simpler approach
                fixed_xml = etree.tostring(root, encoding='unicode')

            return True, f"Fixed {fixed_count} entries", fixed_xml
        else:
            # No entries needed fixing
            return True, "No entries needed fixing", xml_input

    except Exception as e:
        print(f"Error in fix_missing_elements: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}", xml_input


def print_calibration_info(xml_string: str) -> None:
    """
    Print information about alibrations in the XML.

    Args:
        xml_string: XML string to analyze
    """
    try:
        root = etree.fromstring(xml_string)

        # Find all clusters that might be calibration entries
        all_clusters = root.xpath(".//*[local-name()='Cluster']")
        calibration_entries = []

        # Find those that have a String child with Name="Calibration name"
        for cluster in all_clusters:
            # Use our custom finder for case-insensitive matching
            if find_element_by_name(cluster, 'String', 'Calibration name') is not None:
                calibration_entries.append(cluster)

        if not calibration_entries:
            print("No calibration entries found")
            return

        print(f"Found {len(calibration_entries)} calibration entries")

        for i, cal_entry in enumerate(calibration_entries):
            # Get the calibration name
            cal_name_elem = find_element_by_name(cal_entry, 'String', 'Calibration name')
            cal_name = cal_name_elem.find('Val').text if cal_name_elem is not None and cal_name_elem.find(
                'Val') is not None else f"Entry #{i}"
            print(f"\nCalibration {i + 1}: {cal_name}")

            # Find the Calibration Parameters cluster
            cal_params = find_element_by_name(cal_entry, 'Cluster', 'Calibration Parameters')

            if cal_params is None:
                print("  Missing Calibration Parameters cluster")
                continue

            # Get NumElts
            num_elts = cal_params.find('NumElts')
            print(f"  NumElts: {num_elts.text if num_elts is not None else 'Unknown'}")

            # Check for our target elements
            print("  Has Derate:", "Yes" if find_element_by_name(cal_params, 'Cluster', 'Derate') is not None else "No")
            print("  Has Offset Sens:",
                  "Yes" if find_element_by_name(cal_params, 'Cluster', 'Offset Sens') is not None else "No")
            print("  Has Calib Vol:",
                  "Yes" if find_element_by_name(cal_params, 'DBL', 'Calib Vol') is not None else "No")
            print("  Has Shear Factor:",
                  "Yes" if find_element_by_name(cal_params, 'DBL', 'Shear Factor') is not None else "No")

            # Print Range values
            range_cluster = find_element_by_name(cal_params, 'Cluster', 'Range')
            if range_cluster is not None:
                print("  Range values:")
                range_x = find_element_by_name(range_cluster, 'DBL', 'Range X')
                range_y = find_element_by_name(range_cluster, 'DBL', 'Range Y')
                range_z = find_element_by_name(range_cluster, 'DBL', 'Range Z')

                if range_x is not None and range_x.find('Val') is not None:
                    print(f"    X: {range_x.find('Val').text}")
                if range_y is not None and range_y.find('Val') is not None:
                    print(f"    Y: {range_y.find('Val').text}")
                if range_z is not None and range_z.find('Val') is not None:
                    print(f"    Z: {range_z.find('Val').text}")

            # Print Sensitivity values
            sens_cluster = find_element_by_name(cal_params, 'Cluster', 'Sensitivity')
            if sens_cluster is not None:
                print("  Sensitivity values:")
                sens_x = find_element_by_name(sens_cluster, 'DBL', 'Sens X')
                sens_y = find_element_by_name(sens_cluster, 'DBL', 'Sens Y')
                sens_z = find_element_by_name(sens_cluster, 'DBL', 'Sens Z')

                if sens_x is not None and sens_x.find('Val') is not None:
                    print(f"    X: {sens_x.find('Val').text}")
                if sens_y is not None and sens_y.find('Val') is not None:
                    print(f"    Y: {sens_y.find('Val').text}")
                if sens_z is not None and sens_z.find('Val') is not None:
                    print(f"    Z: {sens_z.find('Val').text}")
            else:
                print("  Missing Sensitivity cluster")

            # Print Offset Sens values if present
            offset_sens = find_element_by_name(cal_params, 'Cluster', 'Offset Sens')
            if offset_sens is not None:
                print("  Offset Sens values:")
                offset_x = find_element_by_name(offset_sens, 'DBL', 'Offset Sens X')
                offset_y = find_element_by_name(offset_sens, 'DBL', 'Offset Sens Y')
                offset_z = find_element_by_name(offset_sens, 'DBL', 'Offset Sens Z')

                if offset_x is not None and offset_x.find('Val') is not None:
                    print(f"    X: {offset_x.find('Val').text}")
                if offset_y is not None and offset_y.find('Val') is not None:
                    print(f"    Y: {offset_y.find('Val').text}")
                if offset_z is not None and offset_z.find('Val') is not None:
                    print(f"    Z: {offset_z.find('Val').text}")
            else:
                print("  Missing Offset Sens cluster")

            # Print Calib Vol if present
            calib_vol = find_element_by_name(cal_params, 'DBL', 'Calib Vol')
            if calib_vol is not None and calib_vol.find('Val') is not None:
                print(f"  Calib Vol: {calib_vol.find('Val').text}")
            else:
                print("  Missing Calib Vol")

            # Print Shear Factor if present
            shear_factor = find_element_by_name(cal_params, 'DBL', 'Shear Factor')
            if shear_factor is not None and shear_factor.find('Val') is not None:
                print(f"  Shear Factor: {shear_factor.find('Val').text}")
            else:
                print("  Missing Shear Factor")

    except Exception as e:
        print(f"Error printing calibration info: {str(e)}")
        import traceback
        traceback.print_exc()


# Test functions with actual XML files
if __name__ == "__main__":
    try:
        with open("PiezoConfigListOld.xml", "r") as f:
            xml_string_old = f.read()

        # Check the structure of the old file
        valid, message, _ = check_structure(xml_string_old)
        print(f"Old file valid: {valid}, Message: {message}")

        # Print info about the old file
        print("\nOld file information:")
        print_calibration_info(xml_string_old)

        # Fix the file if needed
        if not valid:
            fix_result, fix_message, fixed_xml = fix_missing_elements(xml_string_old)
            print(f"\nFix result: {fix_message}")

            if fixed_xml:
                # Save the fixed XML
                with open("PiezoConfigListOld_fixed.xml", "w") as f:
                    f.write(fixed_xml)
                print("Fixed XML saved to PiezoConfigListOld_fixed.xml")

                # Check the fixed structure
                valid, message, _ = check_structure(fixed_xml)
                print(f"Fixed file valid: {valid}, Message: {message}")

                # Print info about the fixed file
                print("\nFixed file information:")
                print_calibration_info(fixed_xml)

        # Also test with the new file for comparison
        with open("PiezoConfigList.xml", "r") as f:
            xml_string_new = f.read()

        # Check the structure of the new file
        valid, message, _ = check_structure(xml_string_new)
        print(f"\nNew file valid: {valid}, Message: {message}")

    except FileNotFoundError:
        print(
            "Please make sure the XML files 'PiezoConfigListOld.xml' and 'PiezoConfigList.xml' are in the current directory.")
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback

        traceback.print_exc()