import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommFeatureRoutingRulesComponent } from './comm-feature-routing-rules.component';

describe('CommFeatureRoutingRulesComponent', () => {
  let component: CommFeatureRoutingRulesComponent;
  let fixture: ComponentFixture<CommFeatureRoutingRulesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommFeatureRoutingRulesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommFeatureRoutingRulesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
