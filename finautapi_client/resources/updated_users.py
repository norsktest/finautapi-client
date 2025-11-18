from typing import Dict, Any, List, Optional


class UpdatedUsers: 
    """Endpoint for updated users"""
    
    def __init__(self, client):
        self.client = client
        self.endpoint = "updated_users"
        
        
    def list(
        self, 
        first_name: Optional[str] = None,
        last_name: Optional[str] = None, 
        persnr: Optional[str] = None,
        encoded_userid: Optional[str] = None,
        employee_alias: Optional[str] = None,
        userroles: Optional[str] = None,
        page: Optional[str] = None
    )   -> Dict[str, Any]:
    
    
        params = {}
        if first_name:
            params['first_name'] = first_name
        if last_name:
            params['last_name'] = last_name 
        if persnr:
            params['persnr'] = persnr 
        if encoded_userid:
            params['encoded_userid'] = encoded_userid
        if employee_alias:
            params['employee_alias'] = employee_alias
        if userroles:
            params['userroles'] = userroles
        if page:
            params['page'] = page
            
            
        return self.client.get(f"{self.endpoint}/", params=params)
        
    
       