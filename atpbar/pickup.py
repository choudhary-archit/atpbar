# Tai Sakuma <tai.sakuma@gmail.com>
import os, time
import threading

##__________________________________________________________________||
class ProgressReportPickup(threading.Thread):
    """A pickup of progress reports.

    This class picks up progress reports and presents them.

    Parameters
    ----------
    queue : multiprocessing.Queue
        The queue through which this class receives progress reports
    presentation :
        The presentation of the reports
    """
    def __init__(self, queue, presentation):
        super().__init__(daemon=True)
        # The daemon makes the functions registered at atexit called
        # even if the pickup is still running

        self.queue = queue
        self.presentation = presentation
        self.last_wait_time = 1.0 # [second]

    def end(self):
        """end the thread

        """
        self.queue.put(None)
        self.join()

    def run(self):
        try:
            self._run_until_the_end_order_arrives()
            self._run_until_reports_stop_coming()
        except EOFError:
            pass

    def _run_until_the_end_order_arrives(self):
        end_order_arrived = False
        while True:
            while not self.queue.empty():
                report = self.queue.get()
                if report is None: # the end order
                    end_order_arrived = True
                    continue
                self._process_report(report)
            if end_order_arrived:
                break
            else:
                self._short_sleep()

    def _run_until_reports_stop_coming(self):
        self.last_time = time.time()
        while self.presentation.active():
            if time.time() - self.last_time > self.last_wait_time:
                break
            while not self.queue.empty():
                report = self.queue.get()
                if report is None:
                    continue
                self.last_time = time.time()
                self._process_report(report)
            self._short_sleep()

    def _process_report(self, report):
        self.presentation.present(report)

    def _short_sleep(self):
        """sleep very briefly

        used to prevent the empty `while` loop from increasing CPU
        loads

        """
        time.sleep(0.001)


##__________________________________________________________________||
