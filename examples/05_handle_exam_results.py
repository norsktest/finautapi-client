#!/usr/bin/env python
"""
Example: Read exam results and competency results

FinAut has two kinds of results for your users:

* Exam results (/results/): FinAut's own exams and update tests
  (Kunnskapsprøve, Oppdateringsprøve, ...). Only monitored modules are
  listed. The API needs persnr or from_date; without either it answers
  with an empty list.
* Competency results (/competency_result/): completed courses registered
  by an LMS against a goal (see 07_record_competency_result.py).

Both filter on the date the result was *finished*, not when it reached
FinAut. A result registered late with an earlier date is missed by a
"since my last run" fetch, so fetch with an overlap and de-duplicate on id.

    FINAUT_CLIENT_ID=... FINAUT_CLIENT_SECRET=... python 05_handle_exam_results.py
    ... python 05_handle_exam_results.py --persnr 12345678901
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import FinAutAPIException


def describe_exam_result(result):
    """One line per exam result."""
    assessment = result.get('assessment') or {}
    codes = sorted({m['code'] for m in assessment.get('modules', [])})
    outcome = 'passed' if result.get('passing_grade') else 'not passed'
    return (f"#{result['id']} user {result['user']}"
            f" ({result.get('employee_alias') or '-'}):"
            f" {assessment.get('name', '?')} [{', '.join(codes)}]"
            f" {result.get('percentage_score')}% {outcome},"
            f" attempt {result.get('attempt_number')},"
            f" finished {result.get('datetime_finished')}")


def describe_competency_result(result):
    """One line per competency result."""
    user = result.get('user') or {}
    return (f"#{result['id']} {user.get('first_name', '')} {user.get('last_name', '')}:"
            f" {result.get('courseinfo')} ({result.get('value')} towards"
            f" {result.get('goal')}), finished {result.get('finished')},"
            f" {result.get('external_system')}/{result.get('external_id')}")


def main():
    """List recent results, or one user's results."""
    parser = argparse.ArgumentParser(description='Read FinAut results.')
    parser.add_argument('--days', type=int, default=30,
                        help='look back this many days (default 30)')
    parser.add_argument('--persnr', help="one user's exam results instead")
    args = parser.parse_args()

    client = FinAutAPIClient(
        client_id=os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here'),
        client_secret=os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here'),
        host=os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no'),
    )

    try:
        if args.persnr:
            print(f'Exam results for {args.persnr[:6]}*****:')
            exams = client.results.get_user_results(persnr=args.persnr)
        else:
            print(f'Exam results finished in the last {args.days} days:')
            exams = client.results.get_recent_results(days=args.days)
        for result in exams:
            print('  ' + describe_exam_result(result))
        print(f'  ({len(exams)} in all)')

        since = (date.today() - timedelta(days=args.days)).isoformat()
        params = {'from_date': since}
        if args.persnr:
            params['persnr'] = args.persnr
        print(f'\nCompetency results finished since {since}:')
        completions = client.get_all('competency_result/', params)
        for result in completions:
            print('  ' + describe_competency_result(result))
        print(f'  ({len(completions)} in all)')

    except FinAutAPIException as e:
        print(f'API error: {e}')
        if e.status_code == 403:
            print('Your API user may lack access to results; ask Norsk Test.')
        sys.exit(1)


if __name__ == '__main__':
    main()
