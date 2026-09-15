from sigma import webhook

c = get_config()  #noqa

def post_save(model, os_path, contents_manager, **kwargs):
    if model["type"] != "notebook":
        return

    # Sends the last cells of the notebook, so the instructor can see who is
    # struggling by looking at the errors.
    webhook.notebook_saved(os_path, model["path"])

c.FileContentsManager.post_save_hook = post_save
