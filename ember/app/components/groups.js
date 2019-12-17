

//Object.size = function(obj) {
//    var size = 0, key;
//    for (key in obj) {
//        if (obj.hasOwnProperty(key)) size++;
//    }
//    return size;
//};
//
//function count(){
//    var c= 0;
//    for(var p in this) if(this.hasOwnProperty(p))++c;
//    return c;
//}
//
//export default Route.extend({
//  ajax: service(),
//
//  model() {
//    return this.ajax.request('/api/clubs/');
//  },
//});

//  lengthObj: computed(obj,function() {
//    var c = 0;
//    for(var p in obj) if(obj.hasOwnProperty(p))++c;
//    return c;
//  })
//});
import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model() {
    return this.ajax.request('/api/clubs/');
  },
});
