import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '1s',
};

export default function () {
  http.get('https://example.com');
  sleep(1);
}

