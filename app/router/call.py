"Call handlers for dynamic router"

from typing import Callable, Optional, Union

from fastapi import Depends
from pydantic import create_model, BaseModel


def create_get_call(in_: Union[dict, list],
                    call_name: Optional[str] = None) -> Callable:
    """Generator of GET handle functions returning dictionary data

    Args:
        in_: dictionary or list containing json data to return by call
        call_name: name of the handle method to give to callable
              and dynamically created query model
    Returns:
        callable: fastapi compatible
    """

    # return in case in_ is not indexable array
    async def non_queryable_api_data():
        "In case in_ is non indexable."
        return in_

    if isinstance(in_, list) and len(in_) > 0 and isinstance(in_[0], dict):
        in_dict_schema = in_[0]
        query_params = {str(k): (Optional[type(v)], None)
                        for k, v in in_dict_schema.items()}

        query_model: BaseModel = create_model("Query",
                                              **query_params)  # type: ignore

        # return in case in_ a is list of dictionaries with some keys
        async def querable_api_data(
                params: query_model = Depends()):  # type: ignore
            """In case in_ is list of dictionaries"""
            set_params = params.dict(exclude_none=True)  # type: ignore
            # TO DO: Consider if deep properties
            # should be accessible using dots
            return [el for el in in_
                    if all(el.get(k) == v
                           for k, v in set_params.items())
                    ]

        out_fn = querable_api_data
    else:
        out_fn = non_queryable_api_data  # type: ignore

    if call_name:
        out_fn.__name__ = call_name

    return out_fn


def json_exception_call(exception: Exception,
                        file_name: str,
                        call_name: Optional[str] = None):
    """Generates GET handle function in case exception happened during
        json loading.

    Args:
        exception: An exception that happened during json opening
        name: name of endpoint / json file without exception.
    Returns:
        callable: fastapi compatible
        name: name of the handle method to give to callable
                and dynamically  created query model
    """
    async def _response():
        return {
                "detail": f"The file {file_name} is not valid json.",
                "error": f"Json decode error: {str(exception)}."
            }

    if call_name:
        _response.__name__ = call_name
    return _response
