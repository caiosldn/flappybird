import logging

class GameLogger:
    def __init__(self, log_file='error.log'):
        self.logger = logging.getLogger('GameLogger')
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            
    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)