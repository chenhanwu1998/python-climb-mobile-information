from reptile_project.gzc_climb import mobile_type
from reptile_project.gzc_climb import evaluate_param
from reptile_project.gzc_climb import zgc_mobile
if __name__ == '__main__':
    mobile_type = mobile_type.m_type()
    mobile_type.climb_m_type()

    zgc_reptile = zgc_mobile.zgc_mobile()
    zgc_reptile.run_reptile(verbose=0)

    mobile_reptile = evaluate_param.mobile_param_evaluate()
    mobile_reptile.run_climb(verbose=0)