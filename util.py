import string
import numpy as np
from PIL import Image as im
import cv2
import easyocr
from sympy.codegen.cnodes import sizeof

min_score = 0.45

# Initialize the OCR reader
reader = easyocr.Reader(['es'], gpu=False)
#print(f"reader del ocr....{reader}")


# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}


def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
                                                'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                # print(results[frame_nmr][car_id])
                if 'car' in results[frame_nmr][car_id].keys() and \
                        'license_plate' in results[frame_nmr][car_id].keys() and \
                        'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()


def license_complies_format(text):
    """
    To keep in mind:
        Colombian car license plate has LLL NNN format. Whereas L stands for Letter and N for Number
        Colombian motorcycles plates has LLL NNL

    :param text:
    :return:
    """
    """

    :param text: 
    :return: 
    """

    """
    Check if the license plate text complies with the required format.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text) != 6:
        return False
    # car license format check
    if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
            (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
            (text[2] in string.ascii_uppercase or text[2] in dict_int_to_char.keys()) and \
            (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
            (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in dict_char_to_int.keys()) and \
            (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in dict_char_to_int.keys()):

        return True
    # motorcycle license format check
    #elif (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
    #        (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
    #        (text[2] in string.ascii_uppercase or text[2] in dict_int_to_char.keys()) and \
    #        (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
    #        (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in dict_char_to_int.keys()) and \
    #        (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()):

    #    return True
    else:
        print(f'Image detected had no colombian valid license format {text}')
        return False


def format_license(text):
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = ''
    mapping = {0: dict_int_to_char, 1: dict_int_to_char, 4: dict_char_to_int, 5: dict_char_to_int,
               2: dict_int_to_char, 3: dict_char_to_int}
    for j in [0, 1, 2, 3, 4, 5]:
        if text[j] in mapping[j].keys():
            license_plate_ += mapping[j][text[j]]
        else:
            license_plate_ += text[j]

    return license_plate_


def read_license_plate(license_plate_crop,thres,max):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.

    """

    detections = reader.readtext(license_plate_crop)
    #print(type(license_plate_crop))
    data = im.fromarray(license_plate_crop)
    data.save(f'./pics/{thres}-{max}-plate-crop-pic.png')
    if detections == []:
        return None, None


    def cleanup_text(text):
        # strip out non-ASCII text so we can draw the text on the image
        # using OpenCV
        return "".join([c if ord(c) < 128 else "" for c in text]).strip()

    for detection in detections:
        bbox, text, score = detection
        if(score<min_score):
            print(f"se descarta el texto {text} por bajo score: {score}")
            continue

        text = text.upper().replace(' ', '')
        text = text.upper()


        if text is not None and score is not None and bbox is not None and len(text) == 6:

            text = cleanup_text(text)

            if license_complies_format(text) and score > min_score:
                print(f"La placa {text} cumple con el formato, tiene un score de {score}")
                return format_license(text), score

    return None, None

