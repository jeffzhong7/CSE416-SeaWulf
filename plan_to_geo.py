import conversion as conv
import recom_to_plan
import sys


def plan_to_geo(districting, plan_name):
    for district in districting.districts.keys():
        conv.write_to_file(
            conv.make_json_feature_collection(
                [districting.districts[district].geometry]
            ), 
            "geojson_output/{}/{}.geojson".format(plan_name, district)
        )

    geometries = []
    for d in districting.districts.values():
        geometries.append(d.geometry)
        
    conv.write_to_file(
        conv.make_json_feature_collection(
            geometries
        ), 
        "geojson_output/{}/{}.geojson".format(plan_name, plan_name)
    )