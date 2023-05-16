import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from PIL import Image, ImageTk

def main(matching_result: dict, planogram: dict, image_filename: str):
    ##### Visualize results
    result = matching_result['matchedResultsPerPosition']

    ## Planogram visualization bboxes
    # Create map from position to LTRB coordinates for visualization
    product_id_to_dims = {}  # map from product ID to width and height
    for product in planogram['Products']:
        product_id_to_dims[product['Id']] = [product['W'], product['H']]
    position_to_coords = {}  # map from position to LTRB coordinates
    for j, pos in enumerate(planogram['Positions']):
        w, h = product_id_to_dims[pos['ProductId']]
        position_to_coords[j] = np.array([[pos['X'], pos['Y']],
                                        [pos['X'], pos['Y'] + h],
                                        [pos['X'] + w, pos['Y'] + h],
                                        [pos['X'] + w, pos['Y']]])

    pix_to_real_ratios = [image_width / planogram['Width'], image_height / planogram['Height']]  # ratio of pixels to real-world units

    # Create (P, 4) matrix `planogram_bboxes` for the LTRB coordinates on the image for each position, in sequential, left to right, top to bottom order
    planogram_bboxes = np.empty((len(planogram['Positions']), 4))
    for i, pos in enumerate(planogram['Positions']):
        w, h = product_id_to_dims[pos['ProductId']]
        planogram_bboxes[i] = [pos['X'], pos['Y'], pos['X'] + w, pos['Y'] + h]
    planogram_bboxes = planogram_bboxes * np.array(pix_to_real_ratios * 2)  # (P, 4) LTRB bounding boxes

    ## Raw predicted visualization bboxes
    combined_objects = product_understanding['products'] + product_understanding['gaps']
    predicted_bboxes = np.empty((len(combined_objects), 4))
    for i, object in enumerate(combined_objects):
        x, y, w, h = list(object['boundingBox'].values())
        predicted_bboxes[i] = x, y, x + w, y + h

    ## Predicted visualization bboxes
    predicted_matched_bboxes = np.empty((len(planogram['Positions']), 4))
    for i, match in enumerate(result):
        x, y, w, h = list(match['detectedObject']['boundingBox'].values())
        predicted_matched_bboxes[i] = x, y, x + w, y + h


    ## Visualization
    # Visualize planogram
    planogram_fig = plt.figure()
    plt.title('Overlaid planogram')
    plt.gca().invert_yaxis()
    img = cv2.imread(image_filename)
    plt.imshow(img[:, :, ::-1], alpha=0.3)

    for gt_pt in planogram_bboxes:
        xs = np.array([gt_pt[0], gt_pt[0], gt_pt[2], gt_pt[2], gt_pt[0]])
        ys = np.array([gt_pt[1], gt_pt[3], gt_pt[3], gt_pt[1], gt_pt[1]])
        plt.plot(xs, ys, c='green')
    plt.axis('off')

    # Visualize predictions
    prediction_fig = plt.figure()
    plt.title('Predicted objects')
    plt.gca().invert_yaxis()
    img = cv2.imread(image_filename)
    plt.imshow(img[:, :, ::-1], alpha=0.3)

    for pr_pt in predicted_bboxes:
        xs = np.array([pr_pt[0], pr_pt[0], pr_pt[2], pr_pt[2], pr_pt[0]])
        ys = np.array([pr_pt[1], pr_pt[3], pr_pt[3], pr_pt[1], pr_pt[1]])
        plt.plot(xs, ys, c='blue', linestyle='dashed')
    plt.axis('off')

    # Visualize matchings
    COLORS = ['red', 'lightsalmon', 'orange', 'yellow', 'green', 'chartreuse', 'blue', 'cyan', 'navy', 'darkcyan', 'mediumpurple', 'violet', 'm', 'white', 'black']
    label_colors = [COLORS[x % len(COLORS)] for x in range(len(result))]

    matchings_fig = plt.figure()
    plt.title('Planogram matching results')
    plt.gca().invert_yaxis()
    img = cv2.imread(image_filename)
    plt.imshow(img[:, :, ::-1], alpha=0.3)

    for i, (gt_pt, pr_pt, color) in enumerate(zip(planogram_bboxes, predicted_matched_bboxes, label_colors)):
        xs = np.array([gt_pt[0], gt_pt[0], gt_pt[2], gt_pt[2], gt_pt[0]])
        ys = np.array([gt_pt[1], gt_pt[3], gt_pt[3], gt_pt[1], gt_pt[1]])
        plt.plot(xs, ys, c=color)
        xs = np.array([pr_pt[0], pr_pt[0], pr_pt[2], pr_pt[2], pr_pt[0]])
        ys = np.array([pr_pt[1], pr_pt[3], pr_pt[3], pr_pt[1], pr_pt[1]])
        plt.plot(xs, ys, c=color, linestyle='dashed')

    handles = [Line2D([0], [0], label='planogram', color='black'),
            Line2D([0], [0], label='predictions', color='black', linestyle='dashed'),
            Line2D([0], [0], label='same color = matched', color='white')]
    plt.legend(handles=handles, handlelength=3, bbox_to_anchor=(0.5, 0), loc='upper center')
    plt.axis('off')
    plt.tight_layout()

    # Window positions and titles
    planogram_fig.canvas.manager.set_window_title('Planogram')
    prediction_fig.canvas.manager.set_window_title('Predictions')
    matchings_fig.canvas.manager.set_window_title('Planogram matching')
    plt.show()


if __name__ == '__main__':
    RESOURCE_ROOT = os.path.join('.', 'resources')
    imgs = [os.path.join(RESOURCE_ROOT, 'sample3.jpg'), os.path.join(RESOURCE_ROOT, 'sample4.jpg')]
    SAMPLE_MAPPING = {'snacks': 0, 'drinks': 1}

    # Display window
    win = Tk()
    TEXT_FONT = 'Segoe UI'
    WIN_W, WIN_H = 1500, 1200
    SPACER = 40
    win.geometry(f"{WIN_W}x{WIN_H}")

    # Set title of page
    def show_title():
        title = Label(win, text='Azure Computer Vision Planogram Compliance Demo', font=(TEXT_FONT, 30)).pack(side='top')
    
    def show_instruction(text):
        instruction = Label(win, text=text, font=(TEXT_FONT, 20)).pack(side='top')

    # Display image on initial page
    def get_cover_image(i):
        img = Image.open(imgs[i])
        w, h = img.size
        if i == 0:
            new_w = int(WIN_W * 0.622) - SPACER
        else:
            new_w = int(WIN_W * 0.378) - SPACER
        new_h = int(new_w / w * h)
        img = img.resize((new_w, new_h))
        return ImageTk.PhotoImage(img)

    # First page code
    scenario = 0
    def select_snacks():
        global scenario
        scenario = SAMPLE_MAPPING['snacks']
        visualization_page()

    def select_drinks():
        global scenario
        scenario = SAMPLE_MAPPING['drinks']
        visualization_page()

    def home_page():
        show_title()
        show_instruction('Select the scenario to compute planogram compliance.')
        
        snacks_image, drinks_image = get_cover_image(0), get_cover_image(1)
        snacks_button = Button(win, command=select_snacks, image=snacks_image).place(x=SPACER//2, y=SPACER*3)
        snacks_label = Label(win, text='snacks scenario', font=(TEXT_FONT, 20)).place(x=snacks_image.width()//2 + SPACER//2 - SPACER*2, y=SPACER*3+snacks_image.height()+SPACER//4)
        drinks_button = Button(win, command=select_drinks, image=drinks_image).place(x=SPACER + snacks_image.width() + SPACER//2, y=SPACER*3)
        drinks_label = Label(win, text='milk scenario', font=(TEXT_FONT, 20)).place(x=SPACER + snacks_image.width() + drinks_image.width()//2 + SPACER//2 - SPACER*2, y=SPACER*3+drinks_image.height()+SPACER//4)
        return snacks_image, drinks_image

    # Product understanding and planogram visualization page
    def visualization_page():
        win.destroy()
        main(index=scenario)

    snacks_image, drinks_image = home_page()
    win.mainloop()