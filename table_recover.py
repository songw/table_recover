import gradio as gr
from ocr.data import *
from ocr.utils import *
from ocr.send_and_receive import *
import cv2
import numpy as np
from PIL import Image
from jinja2 import Environment, FileSystemLoader
import sys, fitz


def combine_lines(lines, angle):
    line_cnt = ""
    dict_cnt = {}
    for line in lines:
        if (angle >= 45 and angle <= 135):
            coord = line.get('coord')
            if coord is None:
                return
            else:
                x = coord[0].get('x')
                cnt = line.get('content')
                dict_cnt[x] = cnt
        elif (angle > 135 and angle < 225):
            coord = line.get('coord')
            if coord is None:
                return
            else:
                y = coord[0].get('y')
                cnt = line.get('content')
                dict_cnt[y] = cnt
        elif (angle >= 225 and angle <= 315):
            coord = line.get('coord')
            if coord is None:
                return
            else:
                x = coord[0].get('x')
                cnt = line.get('content')
                dict_cnt[x] = cnt
        else:
            coord = line.get('coord')
            if coord is None:
                return
            else:
                y = coord[0].get('y')
                cnt = line.get('content')
                dict_cnt[y] = cnt
    
    if (angle >= 45 and angle <= 135):
        sorted_dict = dict(sorted(dict_cnt.items()))
    elif (angle > 135 and angle < 225):
        sorted_dict = dict(sorted(dict_cnt.items(), reverse=True))
    elif (angle >= 225 and angle <= 315):
        sorted_dict = dict(sorted(dict_cnt.items(), reverse=True))
    else:
        sorted_dict = dict(sorted(dict_cnt.items()))
    
    for value in sorted_dict.values():
        line_cnt += value
    
    return line_cnt

def obtain_x_coord(elem):
    return elem.get("coord")[0].get("x")

def obtain_y_coord(elem):
    return elem.get("coord")[0].get("y")


def conver_ocr_result_to_table(file_input):
    print(os.path.splitext(file_input.name)[-1])
    if os.path.splitext(file_input.name)[-1] in ['.png', '.jpg', '.jpeg']:
        image = Image.open(file_input.name)
        ret, buf = cv2.imencode(".jpeg", np.array(image))
        f_data = Image.fromarray(np.uint8(buf)).tobytes()
    elif os.path.splitext(file_input.name)[-1] in ['.pdf']:
        doc = fitz.open(file_input.name)
        pix = doc[0].get_pixmap(dpi=150)
        f_data = pix.tobytes()

    request_data['header']['app_id'] = APPId
    resp = execute(request_url, request_data, "POST", APPId, APIKey, APISecret, f_data)
    final_result = deal_response(resp)

    items = {}
    json_result = json.loads(final_result)
    print(json_result)

    angle = 0

    page = json_result.get("pages")[0]
    if page is None:
        return
    angle = page['angle']

    tables = page.get("tables")
    if tables is None:
        return
    
    if angle >= 45 and angle <= 135:
        tables.sort(key=obtain_x_coord, reverse=False)
    elif angle >= 225 and angle <= 315:
        tables.sort(key=obtain_x_coord, reverse=True)
    elif angle > 135 and angle < 225:
        tables.sort(key=obtain_x_coord, reverse=True)

    total_result = []
    for table in tables:
        rows = table.get("rows")
        if rows is None:
            return
        
        cols = table.get("cols")
        if cols is None:
            return

        cells = table.get("cells")
        if cells is None:
            return 

        for cell in cells:
            row = cell.get("row")
            rowspan = cell.get("rowspan")
            col = cell.get("col")
            colspan = cell.get("colspan")
            lines = cell.get("lines")

            if lines is not None:
                line_cnt = combine_lines(lines, angle)
                if angle <= 315 and angle >= 225:
                    tuple_row_key = (cols+1-col+1-colspan, row)
                    tuple_row_value = (cols+1-col+1-colspan, colspan, row, rowspan, line_cnt)
                    items[tuple_row_key] = tuple_row_value
                elif angle >= 45 and angle <= 135:
                    tuple_row_key = (col, rows+1-row+1-rowspan)
                    tuple_row_value = (col, colspan, rows+1-row+1-rowspan, rowspan, line_cnt)
                    items[tuple_row_key] = tuple_row_value
                elif angle < 215 and angle > 135:
                    tuple_row_key = (rows+1-row+1-rowspan, cols+1-col+1-colspan)
                    tuple_row_value = (rows+1-row+1-rowspan, rowspan, cols+1-col+1-colspan, colspan, line_cnt)
                    items[tuple_row_key] = tuple_row_value
                else:
                    tuple_row_key = (row, col)
                    tuple_row_value = (row, rowspan, col, colspan, line_cnt)
                    items[tuple_row_key] = tuple_row_value
            else:
                if angle <= 315 and angle >= 225:
                    tuple_row_key = (cols+1-col+1-colspan, row)
                    tuple_row_value = (cols+1-col+1-colspan, colspan, row, rowspan, "")
                    items[tuple_row_key] = tuple_row_value
                elif angle >= 45 and angle <= 135:
                    tuple_row_key = (col, rows+1-row+1-rowspan)
                    tuple_row_value = (col, colspan, rows+1-row+1-rowspan, rowspan, "")
                    items[tuple_row_key] = tuple_row_value
                elif angle < 215 and angle > 135:
                    tuple_row_key = (rows+1-row+1-rowspan, cols+1-col+1-colspan)
                    tuple_row_value = (rows+1-row+1-rowspan, rowspan, cols+1-col+1-colspan, colspan, "")
                    items[tuple_row_key] = tuple_row_value
                else:
                    tuple_row_key = (row, col)
                    tuple_row_value = (row, rowspan, col, colspan, "")
                    items[tuple_row_key] = tuple_row_value

        result = []
        if (angle >= 45 and angle <= 135) or (angle <= 315 and angle >= 225):
            for i in range(1, cols+1):
                row = []
                for j in range(1, rows+1):
                    key = (i, j)
                    value = items.get(key)
                    if value is not None:
                        row.append(value)
                result.append(row)
        else:
            for i in range(1, rows+1):
                row = []
                for j in range(1, cols+1):
                    key = (i, j)
                    value = items.get(key)
                    if value is not None:
                        row.append(value)
                result.append(row)
        total_result.append(result)

    file_loader = FileSystemLoader('./')
    env = Environment(loader=file_loader)

    template = env.get_template('table.html')
    output = template.render(tables=total_result)

    return output


with gr.Blocks() as demo:
    with gr.Row():
        inp = gr.File(file_types=[".pdf", ".png", ".jpg", ".jpeg"])
    btn = gr.Button("运行")
    with gr.Row():
        outp = gr.HTML(elem_id="myHeader")
    btn.click(fn=conver_ocr_result_to_table, inputs=inp, outputs=outp)

if __name__ == '__main__':
    demo.launch(server_name="0.0.0.0")
