import { shallow } from 'vue-test-utils';
import test from 'ava';

import AnnotateAndSegment from 'views/AnnotateAndSegment'

test('Should mount and render without issue', (t)=> {
  const wrapper = shallow(AnnotateAndSegment);

  const mainDiv = wrapper.find('#annotate-and-segment').length;

  t.is(mainDiv, 1);
})
