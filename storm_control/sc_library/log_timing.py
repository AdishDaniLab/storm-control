#!/usr/bin/env python
"""
This parses a log file series (i.e. log, log.1, log.2, etc..) and
outputs timing and call frequency information for HAL messages.

Hazen 5/18
"""
from datetime import datetime
import os


pattern = '%Y-%m-%d %H:%M:%S,%f'


class Message(object):
    """
    Storage for the timing of a single message.
    """
    def __init__(self, m_type = None, source = None, time = None, zero_time = None, **kwds):
        super().__init__(**kwds)
        self.created_time = None
        self.m_type = m_type
        self.n_workers = 0
        self.processing_time = None
        self.queued_time = None
        self.source = source
        
        self.temp = self.parseTime(time)

    def created(self, time):
        t_time = self.parseTime()
        self.created_time = (self.temp - t_time).total_seconds()

    def getCreatedTime(self):
        """
        Returns the time when the message was created relative to first
        time in the log file in seconds.
        """
        return self.created_time
        
    def getNWorkers(self):
        """
        Return the number of workers (QRunnables) that were employed
        to process this message.
        """
        return self.n_workers
        
    def getProcessingTime(self):
        """
        Return time to process in seconds.
        """
        return self.processing_time
        
    def getQueuedTime(self):
        """
        Return time queued in seconds.
        """
        return self.queued_time

    def getSource(self):
        """
        Returns the source of a message.
        """
        return self.source
    
    def getType(self):
        """
        Return the message type.
        """
        return self.m_type

    def incNWorkers(self):
        self.n_workers += 1
        
    def isComplete(self):
        """
        Returns true if we have all the timing data for this message.
        """
        return (self.processing_time != None)

    def parseTime(self, time):
        return datetime.strptime(time, pattern)

    def processed(self, time):
        t_time = self.parseTime(time)
        self.processing_time = (t_time - self.temp).total_seconds()
        
    def sent(self, time):
        t_time = self.parseTime(time)
        self.queued_time = (t_time - self.temp).total_seconds()
        self.temp = t_time


def getIterable(dict_or_list):
    """
    Returns an iterable given a dictionary of a list.
    """
    if isinstance(dict_or_list, dict):
        iterable = list(dict_or_list.values())
    elif isinstance(dict_or_list, list):
        iterable = dict_or_list
    else:
        raise Exception("Unknown type '" + str(type(dict_or_list)) + "'")
    
    return iterable


def groupByMsgType(messages, ignore_incomplete = True):
    """
    Returns a dictionary keyed by message type, with a list of one or
    more message objects per message type.
    """
    return groupByX(lambda x : x.getType(),
                    messages,
                    ignore_incomplete)


def groupBySource(messages, ignore_incomplete = True):
    """
    Returns a dictionary keyed by message source, with a list of one or
    more message objects per message source.
    """
    return groupByX(lambda x : x.getSource(),
                    messages,
                    ignore_incomplete)


def groupByX(grp_fn, messages, ignore_incomplete):
    """
    Returns a dictionary keyed by the requested group.
    """
    m_grp = {}
    
    for msg in getIterable(messages):

        # Ignore messages that we don't have all the timing for.
        if msg.isComplete() or not ignore_incomplete:
            m_type = grp_fn(msg)
            if m_type in m_grp:
                m_grp[m_type].append(msg)
            else:
                m_grp[m_type] = [msg]
                
    return m_grp
        

def logTiming(basename):
    """
    Returns a dictionary of Message objects keyed by their ID number.
    """
    zero_time = None
    messages = {}

    for ext in [".5", ".4", ".3", ".2", ".1", ""]:

        fname = basename + ".out" + ext
        if not os.path.exists(fname):
            print(fname, "not found.")
            continue
    
        with open(fname) as fp:
            for line in fp:

                try:
                    [time, command] = map(lambda x: x.strip(), line.split(":hal4000:INFO:"))
                except ValueError:
                    continue

                if zero_time is None:
                    zero_time = time

                # Message queued.
                if (command.startswith("queued,")):
                    [m_id, source, m_type] = command.split(",")[1:]
                    messages[m_id] = Message(m_type = m_type,
                                             source = source,
                                             time = time,
                                             zero_time = zero_time)
                              
                # Message sent.
                elif (command.startswith("sent,")):
                    m_id = command.split(",")[1]
                    messages[m_id].sent(time)

                # Message processed.
                elif (command.startswith("processed,")):
                    m_id = command.split(",")[1]
                    messages[m_id].processed(time)

                elif (command.startswith("worker done,")):
                    m_id = command.split(",")[1]
                    messages[m_id].incNWorkers()
    
    return messages


def processingTime(messages):
    """
    Returns the total processing time for a collection of messages.
    """
    accum_time = 0
    for msg in getIterable(messages):
        if isinstance(msg, list):
            for elt in msg:
                accum_time += elt.getProcessingTime()
        else:
            accum_time += msg.getProcessingTime()
    return accum_time


def queuedTime(messages):
    """
    Returns the total queued time for a a collection of messages.
    """
    accum_time = 0
    for msg in getIterable(messages):
        if isinstance(msg, list):
            for elt in msg:
                accum_time += elt.getQueuedTime()
        else:
            accum_time += msg.getQueuedTime()
    return accum_time


if (__name__ == "__main__"):

    import sys
    
    if (len(sys.argv) != 2):
        print("usage: <log file>")
        exit()

    messages = logTiming(sys.argv[1])
    groups = groupByMsgType(messages)

    print()
    print("All messages:")
    for key in sorted(groups):
        grp = groups[key]
        print(key + ", {0:0d} counts, {1:.3f} seconds".format(len(grp), processingTime(grp)))
    print("Total queued time {0:.3f} seconds".format(queuedTime(groups)))
    print("Total processing time {0:.3f} seconds".format(processingTime(groups)))

    print()
    print("Film messages:")
    groups = groupByMsgType(groupBySource(messages)["film"])
    for key in sorted(groups):
        grp = groups[key]
        print(key + ", {0:0d} counts, {1:.3f} seconds".format(len(grp), processingTime(grp)))
    print("Total processing time {0:.3f} seconds".format(processingTime(groups)))



