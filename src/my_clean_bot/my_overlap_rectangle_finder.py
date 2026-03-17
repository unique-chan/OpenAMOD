from shapely.geometry import Polygon


def intersection_over_self(poly_i, poly_j):
    if poly_i.intersects(poly_j):
        return poly_i.intersection(poly_j).area / poly_i.area
    else:
        return 0


def find_overlap_small_rectangle_ids(df, p):
    assert 0 < p <= 1
    overlap_small_polygon_ids = []
    try:
        polygons = [Polygon([(row[f'x{i}'], row[f'y{i}']) for i in (1, 2, 3, 4)])
                    for _, row in df.iterrows()]
        for i in range(len(polygons)):
            for j in range(len(polygons)):
                if i == j or i in overlap_small_polygon_ids or j in overlap_small_polygon_ids:
                    continue
                # overlap | inclusion
                if intersection_over_self(polygons[i], polygons[j]) >= p:
                    if polygons[i].area > polygons[j].area:
                        overlap_small_polygon_ids.append(j)
                    else:
                        overlap_small_polygon_ids.append(i)
        return list(set(overlap_small_polygon_ids)), None
    except:
        return [], 'Polygon_error'
