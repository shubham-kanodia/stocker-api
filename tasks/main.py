from collection.data_collection import DataCollection
from tasks.price_update import price_update_task
from tasks.watchlist_price_notification import generate_price_notifications
from db.crud_operations import CRUDOperations


def run_all_tasks(data_collection: DataCollection, crud_ops: CRUDOperations):
    print("Started update")

    try:
        price_update_task(data_collection)
        generate_price_notifications(crud_ops)

        crud_ops.add_log("Update complete.")

    except Exception as exp:
        crud_ops.add_log("Failed to update prices")
