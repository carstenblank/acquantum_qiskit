import os
from unittest import TestCase

from providers.acquantum.acquantumconnector import AcQuantumConnector
from providers.acquantum.acquantumjob import AcQuantumJob
from providers.acquantum.acquantumprovider import AcQuantumProvider


class TestAcQuantumJob(TestCase):

    def setUp(self) -> None:
        super().setUp()
        os.environ['ACQ_USER'] = 'sebboer'
        os.environ['ACQ_PWD'] = 'qnpwzHyIIFw33Nw2PBx'
        self.provider = AcQuantumProvider()
        self.provider.load_account()
        self.backends = self.provider.backends()

    def test_job_id(self):
        print(self.backends._provider)
        job = AcQuantumJob(self.backends[0], '100', AcQuantumConnector(), False)
        self.assertEqual(job.job_id(), '100')

    def test_submit(self):
        self.fail()

    def test_cancel(self):
        self.fail()

    def test_result(self):
        self.fail()

    def test__wait_for_result(self):
        self.fail()

    def test__wait_for_job(self):
        self.fail()

    def test__check_for_submission(self):
        self.fail()

    def test_status(self):
        self.fail()

    def test__generate_job_name(self):
        self.fail()

    def test__is_job_queued(self):
        self.fail()

    def test__result_from_job_response(self):
        self.fail()
