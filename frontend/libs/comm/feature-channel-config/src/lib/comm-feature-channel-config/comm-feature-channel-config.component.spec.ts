import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommFeatureChannelConfigComponent } from './comm-feature-channel-config.component';

describe('CommFeatureChannelConfigComponent', () => {
  let component: CommFeatureChannelConfigComponent;
  let fixture: ComponentFixture<CommFeatureChannelConfigComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommFeatureChannelConfigComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommFeatureChannelConfigComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
