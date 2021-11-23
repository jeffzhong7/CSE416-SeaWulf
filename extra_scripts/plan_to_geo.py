import conversion as conv
import recom_to_plan
import sys


def plan_to_geo(districting, plan_name):
    for district in districting.districts.keys():
        conv.write_to_file(
            conv.make_json_feature_collection(
                districting.districts[district].geometry,
                conv.make_props(int(district) - 1)
            ), 
            "geojson_output/{}/{}.geo.json".format(plan_name, district)
        )

if __name__ == "__main__":
    main()