from web.weblogger import info


# @scheduler.task(trigger='interval', id='GridDetailScheduler.update', minutes=10)
def execute_update_holding():
    info('scheduler decorator method execution')
