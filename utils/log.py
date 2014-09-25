import logging
import sys
import signal

# create own loglevel 'important' for showing important information with coloring
# http://stackoverflow.com/a/13638084
IMPORTANT_LEVEL_NUM = 25
logging.addLevelName(IMPORTANT_LEVEL_NUM, "IMPORTANT")
def important(self, message, *args, **kwargs):
    if self.isEnabledFor(IMPORTANT_LEVEL_NUM):
        self._log(IMPORTANT_LEVEL_NUM, message, args, **kwargs)


logging.Logger.important = important

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


logging.Logger.trace = trace

signal.signal(signal.SIGINT, signal.SIG_IGN)


# adapter to dynamically add context information (cluster/host) to log
# messages, if provided
class CustomLogAdapter(logging.LoggerAdapter):
    def debug(self, msg, *args, **kwargs):
        """
        Delegate a debug call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Delegate a info call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Delegate a warning call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Delegate a error call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Delegate a critical call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """
        Delegate a exception call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.exception(msg, *args, **kwargs)

    def important(self, msg, *args, **kwargs):
        """
        Delegate a important call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.important(msg, *args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        """
        Delegate a important call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, args, kwargs = self.process(msg, *args, **kwargs)
        self.logger.trace(msg, *args, **kwargs)

    def process(self, msg, *args, **kwargs):
        if not "extra" in kwargs:
            kwargs["extra"] = dict()

        # convert args from tuple to list so we can modify it
        newargs = list(args)

        # initialize host and cluster with default values
        #host = "local"
        #cluster = "none"

        if len(newargs) == 1:
        	kwargs["extra"]["clusterinfo"] = newargs.pop(0)
        elif len(newargs) == 2:
        	kwargs["extra"]["clusterinfo"] = "%s/%s" % (newargs[1], newargs[0])
        elif len(newargs) == 0:
        	kwargs["extra"]["clusterinfo"] = ""
        else:
        	raise ValueError("Number of arguments provided is not right!")

        # append a dash after the clusterinfo, so it looks nice
        # this is not done with the formatting patterns, as it would not allow us to do this dynamically
        if kwargs["extra"]["clusterinfo"]:
        	kwargs["extra"]["clusterinfo"] += " - "

        # get host and cluster from args, if provided
        #try:
        #    host, cluster = newargs
        #    # remove them from args
        #    newargs.remove(host)
        #    newargs.remove(cluster)
        #except:
        #    pass

        # add host and cluster to kwargs, will be passed to the logger
        #kwargs["extra"]["host"] = host
        #kwargs["extra"]["cluster"] = cluster

        # return the modified arguments
        return msg, [], kwargs

    def setLevel(self, lvl):
    	self.logger.setLevel(lvl)
    	

def initialize_logger(logfile, format_file, format_console):
    """ initialize logging - console """

    l = logging.getLogger()

    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    formatter_file = logging.Formatter(format_file)

    # use a colored formatter
    formatter_console = ColorFormatter(format_console)
    ch.setFormatter(formatter_console)
    fh.setFormatter(formatter_file)

    l.addHandler(ch)
    l.addHandler(fh)

    # custom logger adapter to on-the-fly change the logger information to unclude cluster/host information
    l = CustomLogAdapter(l, None)

    return l

############ Colorformatter #############
# source http://stackoverflow.com/a/2532931, modified

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'   : YELLOW,
    'CRITICAL'  : RED,
    'ERROR'     : RED,
    'IMPORTANT' : GREEN,
    'RED'       : RED,
    'GREEN'     : GREEN,
    'YELLOW'    : YELLOW,
    'BLUE'      : BLUE,
    'MAGENTA'   : MAGENTA,
    'CYAN'      : CYAN,
    'WHITE'     : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"

class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        message   = logging.Formatter.format(self, record)
        if levelname in COLORS.keys():
            color     = COLOR_SEQ % (30 + COLORS[levelname])
            message   = message.replace("$RESET", RESET_SEQ)\
                               .replace("$BOLD",  BOLD_SEQ)\
                               .replace("$COLOR", color)
            for k,v in COLORS.items():
                message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                                 .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                                 .replace("$BG-" + k, COLOR_SEQ % (v+40))
        else:
            message = message.replace("$COLOR", "")
            return message
        return message + RESET_SEQ

