#!/usr/bin/env python
"""
Example: Record a course completion (competency result)

An LMS registers a completed course in FinAut by posting a competency
result for the user. The user is identified by the encrypted user id the
LMS received from the FinAut-login flow (get-user-id), not by persnr.

By default this only prints the payload. Pass --send to post it; that
creates a real result. Posting the same external_system, external_id and
goal again is rejected with a 400.

    FINAUT_CLIENT_ID=... FINAUT_CLIENT_SECRET=... \\
        python 07_record_competency_result.py N3F2A... --goal 12 --reward-type 3
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import FinAutAPIException


def main():
    """Look up goals and reward types, then record one completion."""
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('encrypted_userid', help='from FinAut-login')
    parser.add_argument('--goal', required=True, help='goal id')
    parser.add_argument('--reward-type', required=True, help='reward type id')
    parser.add_argument('--value', type=float, default=1)
    parser.add_argument('--external-id', default='example-completion-1')
    parser.add_argument('--send', action='store_true',
                        help='actually post the result')
    args = parser.parse_args()

    client = FinAutAPIClient(
        client_id=os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here'),
        client_secret=os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here'),
        host=os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no'),
    )

    try:
        # The ids to use for --goal and --reward-type
        print('Goals:', json.dumps(client.get('goals/'), indent=2, ensure_ascii=False))
        print('Reward types:', json.dumps(client.get('reward_types/'), indent=2, ensure_ascii=False))

        completion = dict(
            goal=args.goal,
            reward_type=args.reward_type,
            finished=datetime.date.today(),
            value=args.value,
            courseinfo='Example course',
            content_responsible='Example Provider AS',
            external_system='ExampleLMS',
            external_id=args.external_id,
        )
        if not args.send:
            print('Would record:', completion)
            print('Run again with --send to post it.')
            return

        result = client.competency_results.record_completion(
            args.encrypted_userid, **completion)
        print('Recorded:', json.dumps(result, indent=2, ensure_ascii=False))

    except FinAutAPIException as e:
        print(f'API error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
