import cv2
import json
import argparse


def visualize_result(json_filename, image_filename, output_filename, theshold=0.3):
    # Load the prediction result
    with open(json_filename, 'r') as f:
        result = json.load(f)

    # Visualize result
    img = cv2.imread(image_filename)

    # Loop over the products and draw rectangles for each one
    for product in result['products']:
        if product['classifications'][0]['confidence'] > theshold:
            l, t, w, h = product['boundingBox']['x'], product['boundingBox']['y'], product['boundingBox']['w'], product['boundingBox']['h']
            img = cv2.rectangle(img, (l, t), (l + w, t + h), (0, 255, 0), 5)
            # For better visualization, only show the first 15 characters of the label
            img = cv2.putText(img, product['classifications'][0]['label'][0:15], (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Loop over the gaps and draw rectangles for each one
    for product in result['gaps']:
        if product['classifications'][0]['confidence'] > theshold:
            l, t, w, h = product['boundingBox']['x'], product['boundingBox']['y'], product['boundingBox']['w'], product['boundingBox']['h']
            img = cv2.rectangle(img, (l, t), (l + w, t + h), (255, 0, 0), 5)
            img = cv2.putText(img, 'gap', (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    cv2.imwrite(output_filename, img)


def main():
    parser = argparse.ArgumentParser(description='Visualize prediction results from JSON file and image file.')
    parser.add_argument('result_filename', type=str, help='JSON file containing the prediction results.')
    parser.add_argument('image_filename', type=str, help='Image file used for predictions.')
    parser.add_argument('output_filename', type=str, help='Output rendered image filename.')
    parser.add_argument('-t', '--threshold', type=int, default=0.3, help='Confidence threshold to filter out low confidence prediction, default is 0.3.')
    
    args = parser.parse_args()

    visualize_result(args.result_filename, args.image_filename, args.output_filename, args.threshold)


if __name__ == '__main__':
    main()
