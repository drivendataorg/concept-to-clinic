import { shallow } from 'vue-test-utils';
import test from 'ava';

import AnnotateAndSegment from 'views/AnnotateAndSegment'

test('Should mount and render without issue', (t)=> {
  const wrapper = shallow(AnnotateAndSegment);
  t.is(wrapper.name(), 'annotate-and-segment')

  const mainDiv = wrapper.find('#annotate-and-segment');
  t.not(mainDiv, undefined);

  // NOTE: This is just temporary to validate unit test works
  const routeButton = mainDiv.find('button');
  t.is(routeButton.text(), "Test Validating AnnotateAndSegment route");
})
