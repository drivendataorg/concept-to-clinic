import test from 'ava';

import Store from '@/store'

test('Store has initial valid route /', (t)=> {
  t.is(Store.getFirstValidRoute(), '/');
})

test('Store setRouteResult works, thus first route is then not root', (t)=> {
  Store.setRouteResult('/', { url: 'Something something' })
  t.not(Store.getFirstValidRoute(), '/');
})

test('Store return correct first valid route after non-next mutate', (t)=> {
  Store.setRouteResult('/detect-and-select', { url: 'Something something' })
  t.is(Store.getFirstValidRoute(), '/');
})
