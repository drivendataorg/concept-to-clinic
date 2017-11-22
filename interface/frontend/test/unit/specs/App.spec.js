import { mount } from 'avoriaz';
import test from 'ava';

import App from '@/App'

test('App should mount and render without issue', (t)=> {
  const wrapper = mount(App);

  const appDiv = wrapper.find('#app').length;
  t.is(appDiv, 1);
})
