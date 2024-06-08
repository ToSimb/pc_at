from fastapi import APIRouter, Depends, HTTPException
from deps import get_db_repo


from registration.service import (
    registration_agent_reg_id_scheme,
    re_registration_agent_id_scheme
    )
from registration.schemas import AgentScheme

from myException import MyException427, MyException527

from logger.logger import logger

router = APIRouter(
    prefix="/agent-scheme",
    tags=["Registration Agent"]
)


@router.post("")
def agent_scheme(agent_scheme: AgentScheme, agent_id: int = None, agent_reg_id: str = None, db=Depends(get_db_repo)):
    """
    Метод для регистрации агентов
    """
    all_agent_scheme = {
        "scheme_revision": agent_scheme.scheme_revision,
        "scheme": {
            "metrics": agent_scheme.scheme.metrics,
            "templates": agent_scheme.scheme.templates,
            "item_id_list": agent_scheme.scheme.item_id_list,
            "join_id_list": agent_scheme.scheme.join_id_list,
            "item_info_list": agent_scheme.scheme.item_info_list
        }
    }
    try:
        agent_ids, agents_reg_ids = db.gui_select_agents_reg()
        if len(agents_reg_ids) == 0:
            raise MyException527("JoinScheme not loaded.")
        if agent_id:
            if agent_id in agent_ids:
                agent_reg_id_old, scheme_revision_old_agent = db.reg_sch_select_agent_details2(agent_id)
                if all_agent_scheme["scheme_revision"] > scheme_revision_old_agent:
                    # Перерегистрация
                    agent_scheme_return = re_registration_agent_id_scheme(agent_id, agent_reg_id_old, all_agent_scheme,
                                                                          db)
                    return agent_scheme_return
                else:
                    error_str = f"The old version of scheme_revision is specified for the Agent {agent_id}."
                    db.gui_update_agent_id_error(agent_id, error_str)
                    raise MyException427(error_str)
            else:
                raise MyException427(f"Agent_id '{agent_id}' is not registered.")
        elif agent_reg_id:
            if agent_reg_id in agents_reg_ids:
                check_agent = db.gui_select_check_agent_reg_id(agent_reg_id)
                if check_agent:
                    raise MyException427(f"This agent_reg_id '{agent_reg_id}' is already registered, under agent_id = {check_agent}.")
                else:
                    # Регистрация
                    agent_scheme_return = registration_agent_reg_id_scheme(agent_reg_id, all_agent_scheme, db)
                    return agent_scheme_return
            else:
                raise MyException427(f"There is no such agent_reg_id '{agent_reg_id}' in JoinScheme.")
        else:
            raise MyException427("The required parameters for registering an agent schema are not specified.")


    except MyException427 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=427, detail={"error_msg": error_str})
    except MyException527 as e:
        error_str = str(e)
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

    except KeyError as e:
        error_str = f"KeyError: {e}. Could not find the key in the dictionary."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except ValueError as e:
        error_str = f"ValueError: {e}."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except BlockingIOError:
        error_str = f"Vvk Scheme is busy with another process. Please try again later"
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        raise HTTPException(status_code=527, detail={"error_msg": error_str})
    except Exception as e:
        error_str = f"Exception: {e}."
        logger.error(error_str)
        if agent_id:
            db.gui_update_agent_id_error(agent_id, error_str)
        if agent_reg_id:
            db.gui_update_agent_reg_id_error(agent_reg_id, error_str)
        db.reg_sch_block_false()
        raise HTTPException(status_code=527, detail={"error_msg": error_str})

