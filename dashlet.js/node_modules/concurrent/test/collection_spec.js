var chai = require('chai');
var collections = require('../lib/collections');
var spies = require('chai-spies');

chai.use(spies);
var expect = chai.expect;

var list = [];
for (var i = 0; i < 1000; i++) {
  list.push(i);
}
var err = new Error();

describe('collections', function() {
  describe('#forEach', function() {
    it('should have forEach', function() {
      expect(collections).to.have.property('forEach');
    });

    it('should be fulfilled with the number of elements', function(done) {
      var spy = chai.spy(function() {});
      var iterator = collections.forEach(list, spy);

      iterator.then(function(value) {
        expect(value).to.eql(list.length);
        expect(spy).to.have.been.called.exactly(list.length);
        done();
      });
    });

    it('should reject if the iterator throws an error', function(done) {
      var iterator = collections.forEach(list, function() {
        throw (err);
      });

      iterator.then(null, function(reason) {
        expect(reason).to.eql(err);
        done();
      });
    });
  });

  describe('#every', function() {
    it('should have every', function() {
      expect(collections).to.have.property('every');
    });

    it('should return true if all match', function(done) {
      var predicate = function(num) {
        return num >= 0;
      };
      var every = collections.every(list, predicate);

      every.then(function(value) {
        expect(value).to.eql(list.every(predicate));
        done();
      });
    });

    it('should return false if some do not match', function(done) {
      var predicate = function(num) {
        return num > 0;
      };
      var every = collections.every(list, predicate);

      every.then(function(value) {
        expect(value).to.eql(list.every(predicate));
        done();
      });
    });
  });

  describe('#some', function() {
    it('should have some', function() {
      expect(collections).to.have.property('some');
    });

    it('should return true if any match', function(done) {
      var predicate = function(num) {
        return num === 1;
      };
      var some = collections.some(list, predicate);

      some.then(function(value) {
        expect(value).to.eql(list.some(predicate));
        done();
      });
    });

    it('should return false if none match', function(done) {
      var predicate = function(num) {
        return num === -1;
      };
      var some = collections.some(list, predicate);

      some.then(function(value) {
        expect(value).to.eql(list.some(predicate));
        done();
      });
    });
  });

  describe('#filter', function() {
    it('should have filter', function() {
      expect(collections).to.have.property('filter');
    });

    it('should filter the elements', function(done) {
      var predicate = function(element) {
        return element > 1;
      };
      var filtered = collections.filter(list, predicate);

      filtered.then(function(value) {
        expect(value).to.eql(list.filter(predicate));
        done();
      });
    });
  });

  describe('#map', function() {
    it('should have map', function() {
      expect(collections).to.have.property('map');
    });

    it('should apply to all the elements', function(done) {
      var transform = function(element) {
        return element * 2;
      };
      var mapped = collections.map(list, transform);

      mapped.then(function(value) {
        expect(value).to.eql(list.map(transform));
        done();
      });
    });
  });

  describe('#reverse', function() {
    it('should have reverse', function() {
      expect(collections).to.have.property('reverse');
    });

    it('should apply to all the elements', function(done) {
      var reversed = collections.reverse(list);

      reversed.then(function(value) {
        expect(value).to.eql(list.reverse());
        done();
      });
    });
  });

  describe('#reduce', function() {
    it('should have reduce', function() {
      expect(collections).to.have.property('reduce');
    });

    it('should apply to all the elements', function(done) {
      var transform = function(previous, element) {
        return element * 2;
      };
      var reduced = collections.reduce(list, transform);

      reduced.then(function(value) {
        expect(value).to.eql(list.reduce(transform));
        done();
      });
    });
  });

  describe('#reduceRight', function() {
    it('should have reduceRight', function() {
      expect(collections).to.have.property('reduceRight');
    });

    it('should apply to all the elements', function(done) {
      var transform = function(previous, element) {
        return element * 2;
      };
      var reduced = collections.reduceRight(list, transform);

      reduced.then(function(value) {
        expect(value).to.eql(list.reduceRight(transform));
        done();
      });
    });
  });
});