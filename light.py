import os
import math
import json
import numpy as np

class Vector2(object):

    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

    def __sub__(self, value):
        return Vector2(self.x - value.x, self.y - value.y)

    def __str__(self):
        return '(%s,%s)' % (self.x, self.y)

    def normalize(self):
        norm = math.sqrt(self.x * self.x + self.y * self.y)
        if norm == 0.0:
            return Vector2(0.0, 0.0)
        return Vector2(self.x / norm, self.y / norm)

class Rectangle(object):

    def __init__(self, v0: Vector2, v1: Vector2, v2: Vector2, v3: Vector2):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def __str__(self):
        return '(%s, %s, %s, %s)' % (self.v0, self.v1, self.v2, self.v3)

class LightingDeploy:

    scale = 100.0

    currentProjectPath = ""
    currentProjectInputPath = ""
    polyJsonPath = ""

    def deploy(self,PolygonJson):
        lightIndex = 0
        rtnStr = "{\"PreLight\":["
        # with open("/Users/4dage-imac2/Downloads/testLight.json","r") as f:
        #     PolygonJson = f.read()
        p = json.loads(PolygonJson)
        p_array = p["Polygon"]


        polygons = []
        
        for r_array in p_array:

            if len(r_array) < 3 :
                continue

            polygon = []
            polygon.append(Vector2(r_array[0]['x'], r_array[0]['z']))

            # 逆时针
            # for i in range(1, len(r_array)):
            #     polygon.append(Vector2(r_array[i]['x'], r_array[i]['z']))
            
            # 顺时针
            for i in range(len(r_array) - 1, 0, -1):
                polygon.append(Vector2(r_array[i]['x'], r_array[i]['z']))

            # 精度修复，消除轻微平衡误差问题
            for i in range(len(polygon)):
                f_vert = polygon[i]
                for j in range(i + 1, len(polygon)):
                    vert = polygon[j]
                    if abs(f_vert.x - vert.x) <= 0.1:
                        vert.x = f_vert.x
                    if abs(f_vert.y - vert.y) <= 0.1:
                        vert.y = f_vert.y
                    polygon[j] = vert

            # 剔除同一条线上有多个点的数据
            dir1 = (polygon[0] - polygon[len(polygon) - 1]).normalize()
            for i in range(len(polygon) - 1, 0, -1):
                dir2 = (polygon[i] - polygon[i - 1]).normalize()
                if dir1.x * dir2.x + dir1.y * dir2.y == 1.0:
                    print("[Lighting] 踢了共线 %s" % polygon[i])
                    polygon.pop(i)
                    continue
                else:
                    dir1 = dir2

            # 放大
            for i in range(len(polygon)):
                vert = polygon[i]
                vert.x *= self.scale
                vert.y *= self.scale
                polygon[i] = vert

            polygons.append(polygon)

        step = 0.15 * self.scale
        
        cell_by_row = []
        cell_by_col = []

        scan_by_row_count = 0
        scan_by_col_count = 0

        for polygon in polygons:
            box = self.get_enclosing_rectangle(polygon)

            row = (int)(abs(box.v0.y - box.v1.y) / step)
            col  = (int)(abs(box.v1.x - box.v2.x) / step)
            
            isValid_row = np.zeros((row, col), dtype = np.bool)
            isValid_col = np.zeros((row, col), dtype = np.bool)

            for r in range(0, row):
                for c in range(0, col):
                    pos = Vector2(step / 2 + c * step, step / 2 + r * step)
                    pos.x += box.v1.x
                    pos.y += box.v1.y

                    if not self.is_in_polygon(pos, polygon):
                        isValid_row[r, c] = False
                        isValid_col[r, c] = False
                        continue

                    # if self.is_near_polygon(pos, polygon, step):
                    #     isValid_row[r, c] = False
                    #     isValid_col[r, c] = False
                    #     continue
                    
                    isValid_row[r, c] = True
                    isValid_col[r, c] = True

            for r in range(1, row - 1):
                find_head = True

                for c in range(1, col - 1):
                    cc = -1
                    if find_head:
                        if isValid_row[r, c] == True:
                            find_head = False
                            cc = c
                    else:
                        if isValid_row[r, c] == False or c == col - 1:
                            find_head = True
                            cc = c if isValid_row[r, c] else c - 1

                    if cc >= 0:
                        valid = True

                        if valid and isValid_row[r + 1, cc - 1] and isValid_row[r - 1, cc + 1]:
                            if (not isValid_row[r, cc - 1] and not isValid_row[r - 1, cc]) or (not isValid_row[r + 1, cc] and not isValid_row[r, cc + 1]):
                                valid = False

                        if valid and isValid_row[r + 1, cc + 1] and isValid_row[r - 1, cc - 1]:
                            if (not isValid_row[r, cc + 1] and not isValid_row[r - 1, cc]) or (not isValid_row[r + 1, cc] and not isValid_row[r, cc - 1]):
                                valid = False

                        if not valid:
                            isValid_row[r, cc] = False
                            isValid_col[r, cc] = False

            while True:
                start_r = -1
                start_c = -1
                for r in range(0, row):
                    for c in range(0, col):
                        if isValid_row[r, c] == True:
                            start_r = r
                            start_c = c
                            break
                    if start_c >= 0 or start_r >= 0:
                        break

                if start_r == -1 or start_c == -1:
                    break

                end_r = row
                for r in range(start_r, row):
                    if isValid_row[r, start_c] == False:
                        end_r = r
                        break

                end_c = col
                for c in range(start_c, col):
                    if isValid_row[start_r, c] == False:
                        end_c = c
                        break

                last_row = start_r
                for r in range(start_r, end_r):
                    valid_r = True
                    for c in range(start_c, end_c):
                        if isValid_row[r, c] == False:
                            valid_r = False
                            break
                    if valid_r:
                        for c in range(start_c, end_c):
                            isValid_row[r, c] = False
                        last_row = r
                    else:
                        break

                v0 = Vector2(start_c * step + step / 2 + box.v1.x, last_row * step + step / 2 + box.v1.y)
                v1 = Vector2(start_c * step - step / 2 + box.v1.x, start_r * step - step / 2 + box.v1.y)
                v2 = Vector2(end_c * step + step / 2 + box.v1.x,   start_r * step - step / 2 + box.v1.y)
                v3 = Vector2(end_c * step + step / 2 + box.v1.x,   last_row * step + step / 2 + box.v1.y)

                cell_by_row.append(Rectangle(v0, v1, v2, v3))

                scan_by_row_count += 1

            while True:
                start_r = -1
                start_c = -1
                for r in range(0, row):
                    for c in range(0, col):
                        if isValid_col[r, c] == True:
                            start_r = r
                            start_c = c
                            break
                    if start_c >= 0 or start_r >= 0:
                        break

                if start_r == -1 or start_c == -1:
                    break

                end_r = row
                for r in range(start_r, row):
                    if isValid_col[r, start_c] == False:
                        end_r = r
                        break

                end_c = col
                for c in range(start_c, col):
                    if isValid_col[start_r, c] == False:
                        end_c = c
                        break

                last_col = start_c
                for c in range(start_c, end_c):
                    valid_c = True
                    for r in range(start_r, end_r):
                        if isValid_col[r, c] == False:
                            valid_c = False
                            break
                    if valid_c:
                        for r in range(start_r, end_r):
                            isValid_col[r, c] = False
                        last_col = c
                    else:
                        break

                v0 = Vector2(start_c * step + step / 2 + box.v1.x,  end_r * step + step / 2 + box.v1.y)
                v1 = Vector2(start_c * step - step / 2 + box.v1.x,  start_r * step - step / 2 + box.v1.y)
                v2 = Vector2(last_col * step + step / 2 + box.v1.x, start_r * step - step / 2 + box.v1.y)
                v3 = Vector2(last_col * step + step / 2 + box.v1.x, end_r * step + step / 2 + box.v1.y)

                cell_by_col.append(Rectangle(v0, v1, v2, v3))

                scan_by_col_count += 1
        
        cell_list = cell_by_row if scan_by_row_count <= scan_by_col_count else cell_by_col
        for cell in cell_list:
            
            width = abs(cell.v1.x - cell.v2.x)
            height = abs(cell.v0.y - cell.v1.y)

            min_size = 0.7 * self.scale

            if width < min_size or height < min_size:
                continue

            center = Vector2((cell.v1.x + cell.v2.x) / 2, (cell.v0.y + cell.v1.y) / 2)

            # *********** rect lighting ***********
            h = (height / self.scale - 0.5) * 100
            w = (width / self.scale - 0.5) * 100
            #rect_light_spawn(FVector(-1 * center.x, -1 * center.y, height_ceil - 0.5), FRotator(0, -90, 0), FColor(255, 255, 255), h * w * 60, 800, h, w)

            lighting_intensity_scale = 1.0
            spacing = 2.4 * self.scale
            near_wall = spacing / 2
            row_count = 0
            col_count = 0

            height_subtracting_wall = height - near_wall * 2
            if (height < near_wall * 2 + spacing / 2):
                row_count = 1
                intensity = height / 2 / spacing
                if intensity < lighting_intensity_scale:
                    lighting_intensity_scale = intensity
            else:
                row_count = round(height_subtracting_wall / spacing) + 1

            width_subtracting_wall = width - near_wall * 2
            if width < near_wall * 2 + spacing / 2:
                col_count = 1
                intensity = height / 2 / spacing
                if intensity < lighting_intensity_scale:
                    lighting_intensity_scale = intensity
            else:
                col_count = round(width_subtracting_wall / spacing) + 1
            
            spacing_x = 0.0
            if col_count > 1:
                spacing_x = width_subtracting_wall / (col_count - 1)
            
            spacing_y = 0.0
            if row_count > 1:
                spacing_y = height_subtracting_wall / (row_count - 1)

            #print(row_count)
            #print(col_count)
            start_pos = Vector2(0.0, 0.0)

            if abs(spacing_x) < 0.00001:
                start_pos.x = center.x
            else:
                start_pos.x = cell.v1.x + near_wall
            if abs(spacing_y) < 0.00001:
                start_pos.y = center.y
            else:
                start_pos.y = cell.v1.y + near_wall
            
            
            for x in range(0, col_count):
                for y in range(0, row_count):

                    if rtnStr == "{\"PreLight\":[":
                        pass
                    else:
                        rtnStr += ","

                    lightIndex = lightIndex + 1
                    point_light_pos = Vector2(start_pos.x + x * spacing_x, start_pos.y + y * spacing_y)
                    print("第" + str(lightIndex) + "灯的x:" + str(point_light_pos.x/-100))
                    print("第" + str(lightIndex) + "灯的y:" + str(-3))
                    print("第" + str(lightIndex) + "灯的z:" + str(point_light_pos.y/-100))

                    tmpStr = "{"
                    tmpStr += "\"type\""       + ":"   + "\"pointLight\""                         + ","
                    tmpStr += "\"color\""      + ":"   + "\"#FFFFFF\""                            + ","
                    tmpStr += "\"intensity\""  + ":"   + "2"                                      + ","
                    tmpStr += "\"state\""      + ":"   + "1"                                      + ","
                    tmpStr += "\"other\""      + ":"   + "{\"radius\":0.5}"                       + ","
                    tmpStr += "\"id\""         + ":"   + "\"PointLight" + str(lightIndex) + "\""  + ","
                    tmpStr += "\"position\""   + ":"   + "{"
                    tmpStr += "\"x\""          + ":"   + str(point_light_pos.x/-100) + ","
                    tmpStr += "\"y\""          + ":"   + str(-3) + ","
                    tmpStr += "\"z\""          + ":"   + str(point_light_pos.y/-100)
                    tmpStr += "}"
                    tmpStr += "}"

                    rtnStr += tmpStr
        
                    # *********** point lighting ***********
                    # if nightMode:
                    #     point_light_spawn(FVector(-1 * point_light_pos.x, -1 * point_light_pos.y, height_ceil - 130), FRotator(0, 0, 0), FColor(255, 242, 232), 150000, 500, 0)                  
                    # else:
                    #     point_light_spawn(FVector(-1 * point_light_pos.x, -1 * point_light_pos.y, height_ceil - 130), FRotator(0, 0, 0), FColor(255, 255, 255), 200000, 500, 0)
        rtnStr += "]}"
        print("rtnStr:" + rtnStr)
        return rtnStr      

    def is_in_polygon(self, p0 : Vector2, polygon):
        counter = 0
        xinters = 0.0
        p1 : Vector2
        p2 : Vector2
        n = len(polygon)
        p1 = polygon[0]
        for i in range(1, n + 1):
            p2 = polygon[i % n]
            if p0.y > min(p1.y, p2.y) and p0.y <= max(p1.y, p2.y):
                if p0.x < max(p1.x, p2.x):
                    if p1.y != p2.y:  # 线段不平行于X轴 
                        xinters = (p0.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
                        if p1.x == p2.x or p0.x <= xinters:
                            counter += 1
            p1 = p2

        if (counter % 2 == 0):
            return False
        else:
            return True

    def is_near_polygon(self, p0 : Vector2, polygon, limit : float):
        n = len(polygon)
        for i in range(0, n):
            i1 = i
            i2 = (i + 1 if i + 1 < n else 0)
            p1 = polygon[i1]
            p2 = polygon[i2]
            a = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)  # 线段的长度
            b = math.sqrt((p1.x - p0.x)**2 + (p1.y - p0.y)**2)  # p1到p0的距离
            c = math.sqrt((p2.x - p0.x)**2 + (p2.y - p0.y)**2)  # p2到p0的距离

            # 点到线段两端的距离少于limit
            if (b <= limit or c <= limit):
                return True

            # 线段本身很短
            if a <= 0.001:
                return True

            # 点在延长线的两边
            if b * b >= a * a + c * c:
                if c <= limit:
                    return True
                continue
            if c * c >= a * a + b * b:
                if b <= limit:
                    return True
                continue

            p = (a + b + c) / 2 # 半周长
            s = math.sqrt(p * (p - a) * (p - b) * (p - c)) # 海伦公式求面积
            dis = 2 * s / a   # 返回点到线的距离（利用三角形面积公式求高)
            if limit - dis > 0.0001 * self.scale:
                return True
        return False

    def get_enclosing_rectangle(self, polygon):
        
        x_max = y_max = -99999.0
        x_min = y_min = 99999.0

        for i in range(len(polygon)):
            tx = polygon[i].x
            ty = polygon[i].y
            if tx >= x_max:
                x_max = tx
            if ty >= y_max:
                y_max = ty
            if tx <= x_min:
                x_min = tx
            if ty <= y_min:
                y_min = ty
        
        v0 = Vector2(x_min, y_max)
        v1 = Vector2(x_min, y_min)
        v2 = Vector2(x_max, y_min)
        v3 = Vector2(x_max, y_max)

        result = Rectangle(v0, v1, v2, v3)
        return result

# light spawn
# def point_light_spawn(position, rotation, color, intensity : float, attenuation_radius : float, source_length : float):
#     ue.get_editor_world().point_light_spawn(position, rotation, color, intensity, attenuation_radius, source_length)

# def spot_light_spawn(position, rotation,  color, intensity : float, attenuation_radius : float):
#     ue.get_editor_world().spot_light_spawn(position, rotation, color, intensity, attenuation_radius)

# def rect_light_spawn(position, rotation,  color, intensity : float, attenuation_radius : float, source_width : float, source_height : float):
#     ue.get_editor_world().rect_light_spawn(position, rotation, color, intensity, attenuation_radius, source_width, source_height)



#    run
# deploy = LightingDeploy()
# deploy.deploy("")