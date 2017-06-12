__author__ ='robusgauli@gmail.com'

import os
import sys
import collections
import re
import json
import functools
import itertools

from flask import jsonify
from flask import request

from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import DataError

from restfulapigen.envelop import (
    fatal_error_envelop,
    json_records_envelop,
    record_updated_envelop,
    record_created_envelop,
    record_notfound_envelop,
    record_exists_envelop,
    record_deleted_envelop,
    data_error_envelop,
    validation_error_envelop
)

from restfulapigen.errors import (
    PrimaryKeyNotFound
)


format_error = lambda _em : \
                    re.search(r'\n.*\n', _em).group(0).strip().capitalize()

format_data_error = lambda _em : \
                    re.search(r'\).*\n', _em).group(0)[1:].strip().capitalize()

valid_file = lambda v_file : os.path.exists(v_file) \
                    and os.path.isfile(v_file) and os.path.splitext(v_file)[1] == '.json'



def new_method(model_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            model_name = func
            return model_name(*args, **kwargs)
        return wrapper
    return decorator





class RESTApi:

    def __init__(self, app, db_session, validation_file = None):
        self.app = app
        self.db_session = db_session
        
        if validation_file is not None and valid_file(validation_file):
            #this is valid json file
            self._validation = json.loads(open(validation_file).read())
        else:
            self._validation = None
        
            
    def get_for(self, model, 
                    before_response_for_resources=None, 
                    before_response_for_resource=None, *, 
                    extract=None,
                    relationship=False,
                    extractfor_resources=None):

        if not model.__mapper__.primary_key:
            raise PrimaryKeyNotFound('Primary key not found in % table' % model.__tablename__)
    
        _primary_key = model.__mapper__.primary_key[0].name
        
        if extract:
            extract = list(extract)
        
        def _get_resources():
            results = self.db_session.query(model).all()
            
            if not extractfor_resources:
                print('appyfor resource false')
                _list_data_exp = ({key: val for key, val in vars(r).items()
                                    if not key.startswith('_')
                                    } for r in results)
                #inject the URI to the data
                _list_data = list({**adict, 'uri' : '/%s/%s' % (model.__tablename__, adict[_primary_key])}
                                for adict in _list_data_exp)
                #if after request if not not then call the predicate
                if before_response_for_resources:
                    before_response_for_resources(_list_data)
            
                return json_records_envelop(_list_data)
            else:
                _extractfor_resources = list(extractfor_resources)
                
                _list_data = []
                for result in results:
                    _adict = {key:val for key, val in vars(result).items() if not key.startswith('_')}
                    adict = {**_adict, 'uri' : '/%s/%s' % (model.__tablename__, _adict[_primary_key])}
                    #nod for each extract with the many to one relationship,
                    for relationship in _extractfor_resources:
                        _rel_val = getattr(result, relationship)
                        if not _rel_val:
                            adict[relationship] = None
                            continue
                        if not isinstance(_rel_val, collections.Iterable):
                            adict[relationship] = {key: val for key, val in vars(_rel_val).items()
                                                                    if not key.startswith('_')}
                            continue
                        
                        adict[relationship] = list({key: val for key, val in vars(_r_val).items()
                                                                    if not key.startswith('_')}
                                                                    for _r_val in _rel_val)
                                                                    

                    #finally add to the list
                    _list_data.append(adict)
                return json_records_envelop(_list_data)

        _get_resources.__name__ = 'get_all' + model.__tablename__ 

        self.app.route('/%s' % model.__tablename__)(_get_resources)

        
        def _get_resource(r_id):
            try:

                result = self.db_session.query(model).\
                            filter(getattr(model, _primary_key) == r_id).one()
                _data = {
                    key : val for key, val in vars(result).items()
                    if not key.startswith('_')
                }

                if before_response_for_resource:
                    before_response_for_resource(result, _data)
                
                if extract:
                    for relationship in extract:
                        #get the attribute
                        children = getattr(result, relationship)
                        if not children:
                            _data[relationship] = None
                            continue
                        if not isinstance(children, collections.Iterable):
                            #that means it is on many to one side
                            _data[relationship] = {key: val for key, val in
                                                    vars(children).items() if not
                                                    key.startswith('_')}
                            continue
                        
                        _data[relationship] = list({key : val for key, val 
                                                    in vars(child).items() if not
                                                    key.startswith('_')} for child in children)
                        
                
            except NoResultFound:
                return record_notfound_envelop()
            else:
                
                return json_records_envelop(_data)
        _get_resource.__name__ = 'get' + model.__tablename__

        self.app.route('/%s/<int:r_id>' % model.__tablename__)(_get_resource)

        if relationship:
            #loads the relationship information
            self.db_session.query(model)
            ##get the relatioship atributes with the direction having 'ONE TO MANY'

            _props = list(attr for attr, rel_prop in 
                                    model.__mapper__._props.items() if isinstance(rel_prop, RelationshipProperty) 
                                    and rel_prop.direction.name == 'ONETOMANY')
            
                
            
            for _prop in _props:
                #create a nested uri for the each _prop 
                
                def _get_resources_by_parent(id):
                    try:
                        parent = self.db_session.query(model).\
                                    filter(getattr(model, _primary_key) == id).one()
                    except NoResultFound:
                        return record_notfound_envelop()
                    else:
                        _results = getattr(parent, _prop)
                        _list = list({key : val for key, val in vars(data).items() if not key.startswith('_')}
                                        for data in _results)
                        return json_records_envelop(_list)



                _get_resources_by_parent.__name__ = 'get' + model.__tablename__ + 'by' + _prop
                self.app.route('/%s/<int:id>/%s' % (model.__tablename__, _prop))(_get_resources_by_parent)
                    
    
    def update_for(self, model, 
                    before_response_for_resource=None):
        if not model.__mapper__.primary_key:
            raise PrimaryKeyNotFound('Primary key not found in % table' % model.__tablename__)
    
        _primary_key = model.__mapper__.primary_key[0].name
        
        def _update_resource(id):
            try:
                self.db_session.query(model).filter(getattr(model, _primary_key) == id).update(request.json)
                self.db_session.commit()
            except IntegrityError as e:
                return record_exists_envelop(format_error(str(e)))
            except DataError as e:
                return data_error_envelop(format_data_error(str(e)))
            else:
                return record_updated_envelop(request.json)

        _update_resource.__name__ = 'put' + model.__tablename__
        #add the route 
        self.app.route('/%s/<int:id>' % model.__tablename__, methods=['PUT'])(_update_resource)
    

    def post_for(self, model):

        def _post():
            if self._validation and model.__name__ in self._validation:
                valid, err = validate(self._validation[model.__name__], request.json)
                if not valid:
                    return validation_error_envelop(err)
            try:
                self.db_session.add(model(**request.json))
                self.db_session.commit()
            
            except IntegrityError as e:
                self.db_session.rollback()
                return record_exists_envelop(format_error(str(e)))
            except DataError as e:
                self.db_session.rollback()
                return data_error_envelop(format_data_error(str(e)))
            else:
                return record_created_envelop(request.json)
        
        #change the name of the function 
        _post.__name__ = 'post' + model.__tablename__
        self.app.route('/%s' % model.__tablename__, methods=['POST'])(_post)
    
    def delete_for(self, model):

        if not model.__mapper__.primary_key:
            raise PrimaryKeyNotFound('Primary Key Not Found in %s table' % model.__tablename__)
        
        #get the primary_key
        _primary_key = model.__mapper__.primary_key[0].name
        def _delete(id):
            try:
                _resource = self.db_session.query(model).filter(getattr(model, _primary_key) == id).one()
                self.db_session.delete(_resource)
                self.db_session.commit()
            except NoResultFound:
                
                return record_notfound_envelop()
            else:
                return record_deleted_envelop()
        
        _delete.__name__ = 'delete_' + model.__tablename__

        self.app.route('/%s/<int:id>' % model.__tablename__, methods=['DELETE'])(_delete)
    

    def rest_for(self, model, *, extract=None,
                                 relationship=False, 
                                 extractfor_resources=False, 
                                 before_response_for_resources=None,
                                 before_response_for_resource=None):
        '''Apply all the http methods for the resources'''

        self.get_for(model, extract=extract, 
                            relationship=relationship,
                            extractfor_resources=extractfor_resources,
                            before_response_for_resources=before_response_for_resources,
                            before_response_for_resource=before_response_for_resource)
        self.post_for(model)
        self.delete_for(model)
        self.update_for(model)




def validate(validation, data):
    #get all the keys from data that are to be validated
    _keys = list(data.keys() & validation.keys())

    for key in _keys:
        #get the val
        _val = data[key]
        
        if validation[key].get('not_null', None) and _val is None:
            return False, 'Value for key %r cannot be Null/None' %(key)

        if isinstance(_val, int):
            if validation[key].get('max_val', None) and _val >= validation[key]['max_val']:
                return False, 'Integer value for %r cannot be greater than  %s' % (key, validation[key]['max_val'])
            
            if validation[key].get('min_val', None) and _val <= validation[key]['min_val']:
                return False, 'Integer value for %r cannot be less than %s' %(key, validation[key]['min_val'])
    
        if validation[key].get('max_len', None) and not len(str(_val)) <= validation[key]['max_len']:
            return False, 'Value for key %r cannot have length more than %s' % (key, validation[key]['max_len'])
        
        if validation[key].get('min_len', None) and not len(str(_val)) >= validation[key]['min_len']:
            return False, 'Value for key %r cannot have length less than %s' % (key, validation[key]['min_len'])
        
        
    
    return True, None
    
